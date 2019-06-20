# Common features for all types of test
import os
import requests
import json
import copy_of_main_constants_do_not_edit as constants
import bcrypt
from base64 import b64decode
import copy

securityTestAPIEndpoint = '/securityTestEndpoint'

#THESE ARE DIFFERENT THAN IN TEST HELPER SUPERCLASS
## They are reversed because container test go through nginx which switches them abound
loginAPIPrefix = '/public/api/login'
adminAPIPrefix = '/authed/api/admin'


baseURL="http://saas_user_management_system:80"
if ('BASEURL_TO_TEST' in os.environ):
  baseURL=os.environ['BASEURL_TO_TEST']
runningViaKong = False
if ('RUNNINGVIAKONG' in os.environ):
  runningViaKong=True


httpOrigin = "http://localhost"
if ('HTTPORIGIN_TO_TEST' in os.environ):
  httpOrigin=os.environ['HTTPORIGIN_TO_TEST']


BASE = [0,1,2,3,4]
LOGIN = 0
ADMIN = 1
APIDOCS = 2
FRONTEND = 3
ADMINFRONTEND = 4
BASE[LOGIN]=baseURL + loginAPIPrefix
BASE[ADMIN]=baseURL + adminAPIPrefix
BASE[APIDOCS]=baseURL + '/public/web/apidocs'
BASE[FRONTEND]=baseURL + '/public/web/frontend'
BASE[ADMINFRONTEND]=baseURL + '/public/web/adminfrontend'

def getEnviromentVariable(name):
  return readFromEnviroment(os.environ, name, None, None, False)

#Read environment variable or raise an exception if it is missing and there is no default
def readFromEnviroment(env, envVarName, defaultValue, acceptableValues, nullValueAllowed=False):
  val = None
  if envVarName not in env:
    if envVarName.startswith("APIAPP_"):
      if envVarName + "FILE" in env:
        print("Reading param from file for " + envVarName)
        if not os.path.isfile(env[envVarName + "FILE"]):
          raise Exception('FILE version of enviroment set but file not found - ' + envVarName + ' file:' + env[envVarName + "FILE"])
        with open(env[envVarName + "FILE"], 'r') as file:
            val = file.read()
  if val is None:
    try:
      val = env[envVarName]
    except KeyError:
      if (defaultValue == None):
        raise Exception('Enviroment variable not set (Normal or FILE version) - ' + envVarName)
      return defaultValue

  if (acceptableValues != None):
    if (val not in acceptableValues):
      raise getInvalidEnvVarParamaterException(envVarName, val, 'Not an acceptable value')
  if not nullValueAllowed:
    if val == '':
      raise getInvalidEnvVarParamaterException(envVarName, None, 'Null/Empty String')
  return val

def getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(username, password, tenantAuthProvSalt):
  masterSecretKey = (username + ":" + password + ":AG44")
  decodedSalt = b64decode(tenantAuthProvSalt)
  ret = bcrypt.hashpw(masterSecretKey.encode('utf-8'), decodedSalt)
  return ret.decode("utf-8")


def _callService(api, url, method, dataDICT, expectedResponses, loginDICT, headers, cookies):
  _headers = {}
  if headers is not None:
    _headers = copy.deepcopy(headers)
  _cookies = {}
  if cookies is not None:
    _cookies = copy.deepcopy(cookies)

  _headers["Origin"] = httpOrigin
  result = None
  targetURL = BASE[api] + url
  if loginDICT is not None:
    #print(loginDICT['jwtData']['JWTToken'])
    _headers[constants.jwtHeaderName] = loginDICT['jwtData']['JWTToken']

  if method=='get':
    result = requests.get(
      targetURL,
      headers=_headers,
      cookies=_cookies
    )
  if method=='post':
    _headers['content-type'] = 'application/json'
    result = requests.post(
      targetURL,
      data=json.dumps(dataDICT),
      headers=_headers,
      cookies=_cookies
    )
  if method=='put':
    _headers['content-type'] = 'application/json'
    result = requests.put(
      targetURL,
      data=json.dumps(dataDICT),
      headers=_headers,
      cookies=_cookies
    )
  if result.status_code not in expectedResponses:
    print("Sending " + method + " to ", targetURL)
    if dataDICT is not None:
      print(" data:", dataDICT)
    print("Got response ",result.status_code)
    print("     ",result.text)
    raise Exception("Did not get expected response")
  if api in [LOGIN, ADMIN]:
    return json.loads(result.text), result.status_code
  return result.text, result.status_code


def callGetService(api,url, expectedResponses, loginDICT, headers, cookies):
  return _callService(api,url, "get", None, expectedResponses, loginDICT, headers, cookies)

def callPostService(api,url, POSTdict, expectedResponses, loginDICT, headers, cookies):
  return _callService(api,url, "post", POSTdict, expectedResponses, loginDICT, headers, cookies)

def callPutService(api,url, PUTdict, expectedResponses, loginDICT, headers, cookies):
  return _callService(api,url, "put", PUTdict, expectedResponses, loginDICT, headers, cookies)

def getLoginDICTForDefaultUser(unittestClassInstance):
  AuthProvidersDICT,res = callGetService(
    LOGIN, "/" + constants.masterTenantName + "/authproviders",
    [200],
    None,
    None,
    None
  )
  MainAuthProvider = AuthProvidersDICT['AuthProviders'][0]

  loginCallDICT = {
    "authProviderGUID": MainAuthProvider['guid'],
    "credentialJSON": {
      "username": getEnviromentVariable('APIAPP_DEFAULTHOMEADMINUSERNAME'),
      "password": getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(
        getEnviromentVariable('APIAPP_DEFAULTHOMEADMINUSERNAME'),
        getEnviromentVariable('APIAPP_DEFAULTHOMEADMINPASSWORD'),
        MainAuthProvider['saltForPasswordHashing']
      )
     }
  }
  ###print("Login DICT:",loginCallDICT)
  loginDICT,res = callPostService(LOGIN, "/" + constants.masterTenantName + "/authproviders",loginCallDICT,[200], None, None, None)
  return loginDICT
