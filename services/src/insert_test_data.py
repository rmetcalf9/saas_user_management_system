#Python script to insert test data to a running instance
from constants import masterTenantName, jwtHeaderName, masterTenantDefaultSystemAdminRole
import requests
import json
import os
import bcrypt
from base64 import b64decode
import copy
import time


env = os.environ
BASE = [0,1]
LOGIN = 0
ADMIN = 1
BASE[LOGIN]="http://127.0.0.1:8098/api/public/login"
BASE[ADMIN]="http://127.0.0.1:8098/api/authed/admin"

loginDICT = None #Global, header automatically added to calls when credentials are present

def getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(username, password, tenantAuthProvSalt):
  masterSecretKey = (username + ":" + password + ":AG44")
  decodedSalt = b64decode(tenantAuthProvSalt)
  ret = bcrypt.hashpw(masterSecretKey.encode('utf-8'), decodedSalt)
  return ret.decode("utf-8") 

def callService(api, url, method, dataDICT, expectedResponses):
  result = None
  targetURL = BASE[api] + url
  headers = {}
  data = None
  if loginDICT is not None:
    #print(loginDICT['jwtData']['JWTToken'])
    headers[jwtHeaderName] = loginDICT['jwtData']['JWTToken']
  requestsFn = None
  if method=='get':
    requestsFn = requests.get
  if method=='post':
    headers['content-type'] = 'application/json'
    data=json.dumps(dataDICT)
    requestsFn = requests.post
  if method=='put':
    headers['content-type'] = 'application/json'
    data=json.dumps(dataDICT)
    requestsFn = requests.put

  numTries = 0
  unsucessful = True
  while unsucessful:
    unsucessful = False
    if numTries > 0:
      print(" Call failed (try " + str(numTries) + ") - retrying...")
      time.sleep(1)
    numTries = numTries + 1
    try:
      result = requestsFn(
        targetURL,
        data=data,
        headers=headers
      )
    except Exception as err:
      unsucessful = True
      if numTries > 60:
        print("We have been trying too many times - giving up")
        raise err 
      

  if result.status_code not in expectedResponses:
    print("Sending " + method + " to ", targetURL)
    if dataDICT is not None:
      print(" data:", dataDICT)
    print("Got response ",result.status_code)
    print("     ",result.text)
    raise Exception("Did not get expected response")
  return json.loads(result.text), result.status_code
  
  
def callGetService(api,url, expectedResponses):
  return callService(api,url, "get", None, expectedResponses)

def callPostService(api,url, POSTdict, expectedResponses):
  return callService(api,url, "post", POSTdict, expectedResponses)

def callPutService(api,url, PUTdict, expectedResponses):
  return callService(api,url, "put", PUTdict, expectedResponses)

#Called when there is an error in the process
def errorInProcess(errMessage):
  print("Error in process - halting")
  print(" Msg:", errMessage)
  print("")
  print("Press Enter to exit")
  a = input()
  exit(1)
  

print("Start of script to insert test data")

AuthProvidersDICT,res = callGetService(LOGIN, "/" + masterTenantName + "/authproviders", [200])
MainAuthProvider = AuthProvidersDICT['AuthProviders'][0]

loginCallDICT = {
  "authProviderGUID": MainAuthProvider['guid'],
  "credentialJSON": { 
    "username": env['APIAPP_DEFAULTHOMEADMINUSERNAME'], 
    "password": getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(env['APIAPP_DEFAULTHOMEADMINUSERNAME'], env['APIAPP_DEFAULTHOMEADMINPASSWORD'], MainAuthProvider['saltForPasswordHashing'])
   }
}
loginDICT,res = callPostService(LOGIN, "/" + masterTenantName + "/authproviders",loginCallDICT,[200])

tenantCreationDICT = {
  "Name": "testData_Tenant",
  "Description": "Created by insert_test_data.py",
  "AllowUserCreation": True,
  "AuthProviders": []
}

authProvCreationDICT = {
    "guid": None,
    "Type": "internal",
    "AllowUserCreation": True,
    "MenuText": "Login with Local Account",
    "IconLink": "string",
    "ConfigJSON": "{\"userSufix\": \"@testUserSufix\"}",
    "saltForPasswordHashing": None
}

authProvGoogleCreationDICT = {
    "guid": None,
    "Type": "google",
    "AllowUserCreation": True,
    "MenuText": "Login with Google",
    "IconLink": "string",
    "ConfigJSON": "{\"clientSecretJSONFile\":\"" + os.path.dirname(os.path.realpath(__file__)) + "/../googleauth_client_secret.json\"}",
    "saltForPasswordHashing": None
}

#print(authProvGoogleCreationDICT)
#errorInProcess("DD")

registeruserDICT = {
  "authProviderGUID": "TODO",
  "credentialJSON": { 
    "username": "testUser_", 
    "password": getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(env['APIAPP_DEFAULTHOMEADMINUSERNAME'], env['APIAPP_DEFAULTHOMEADMINPASSWORD'], MainAuthProvider['saltForPasswordHashing'])
   }
}

def createUserUsingAdminAPI(UserID, known_as, mainTenant):
  print(" - creating user " + UserID + " on " + mainTenant + ' ', end='')
  postDict = {"UserID":UserID,"known_as":known_as,"mainTenant":mainTenant}
  resDICT, res = callPostService(ADMIN, "/" + masterTenantName + "/users", postDict,[201, 400])
  if (res==400):
    if (resDICT['message'] == 'That username is already in use'):
      print('Skipping as it already exists', end='')
    else:
      print("")
      print("ERROR ERROR ERROR")
      print(res)
      print(resDICT)
      raise Exception()
  print(".")

def getTenantRoleDictFromTenantRoles(tenantRoles, tenantName):
  for x in tenantRoles:
    if x["TenantName"] == tenantName:
      return x
  a = {
    "TenantName": tenantName,
    "ThisTenantRoles": []
  }
  tenantRoles.append(a)
  return a
  
def addUserRole(UserID, TenantName, role):
  print(" - adding " + role + " role to " + UserID + " on " + TenantName + " ", end='')
  AuthProvidersDICT,res = callGetService(ADMIN, "/" + masterTenantName + "/users/" + UserID, [200])
  #only works with existing tenant. When we need to add tenant will expand code
  tenantRoleDict = getTenantRoleDictFromTenantRoles(AuthProvidersDICT["TenantRoles"], TenantName)
  tenantRoleDict["ThisTenantRoles"].append(role)
  #print("\ninsert data addUserRole Got:******************************")
  #print(AuthProvidersDICT)
  tenantDICT, res = callPutService(ADMIN, "/" + masterTenantName + "/users/" + UserID, AuthProvidersDICT, [200])
  print(".")

def createPersonUsingAdminAPI():
  print(" - creating person ", end='')
  postDict = {}
  resDICT, res = callPostService(ADMIN, "/" + masterTenantName + "/persons", postDict,[201])
  print(' - new person GUID=' + resDICT['guid'])
  return resDICT

def linkUserAndPerson(UserID, personGUID):
  print(" - creating person link between " + UserID + " and " + personGUID + ' ', end='')
  postDict = {"UserID":UserID,"personGUID":personGUID}
  resDICT, res = callPostService(ADMIN, "/" + masterTenantName + "/userpersonlinks/" + UserID + "/" + personGUID, postDict,[201])
  print(".")

def addInternalAuth(personGUID, tenantName, authProvider, username, password):
  hashedPassword = getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(username, password, authProvider['saltForPasswordHashing'])
  print(" - adding admin2 internal auth for " + personGUID + " ", end='')
  postDict = {"personGUID":personGUID,"tenantName":tenantName,"authProviderGUID":authProvider['guid'],"credentialJSON":{"username":username,"password":hashedPassword}}
  resDICT, res = callPostService(ADMIN, "/" + masterTenantName + "/auths", postDict,[201, 400])
  if (res==400):
    if (resDICT['message'] == 'That username is already in use'):
      print('Skipping as it already exists', end='')
    else:
      print("")
      print("ERROR ERROR ERROR")
      print(res)
      print(resDICT)
      raise Exception()
  print('.')

def addAuthProvider(tenantName, authDict):
  tenantDICT, res = callGetService(ADMIN, "/" + masterTenantName + "/tenants/" + tenantName, [200])
  tenantDICT["AuthProviders"].append(authDict)
  tenantDICT2, res = callPutService(ADMIN, "/" + masterTenantName + "/tenants/" + tenantDICT['Name'], tenantDICT, [200])
  if (res==400):
    if (resDICT['message'] == 'Auth PRov exists'):
      print('Skipping add auth prov to tenant ' + tenantName)
    else:
      print(resDICT)
      errorInProcess("Error")
  return tenantDICT2
  
print("Setting up admin2 auth connected to two users - adminTest and normalTest")
createUserUsingAdminAPI("adminTest", "adminTest", masterTenantName)
createUserUsingAdminAPI("normalTest", "normalTest", masterTenantName)
addUserRole("adminTest", masterTenantName, masterTenantDefaultSystemAdminRole)
personDICT = createPersonUsingAdminAPI()
linkUserAndPerson("adminTest", personDICT['guid'])
linkUserAndPerson("normalTest", personDICT['guid'])
addInternalAuth(personDICT['guid'], masterTenantName, MainAuthProvider, 'admin2', 'admin2')

print("Adding google auth to master tenant")
addAuthProvider(masterTenantName, authProvGoogleCreationDICT)

print("Creating allowUserCreation tenants with users created with register method")
for cur in range(4):
  print("Allow User Tenant ", cur)
  creationDICT = copy.deepcopy(tenantCreationDICT)
  creationDICT['Name'] = creationDICT['Name'] + str(cur)
  resDICT, res = callPostService(ADMIN, "/" + masterTenantName + "/tenants", creationDICT,[201, 400])
  if (res==400):
    if (resDICT['message'] == 'Tenant Already Exists'):
      print('Skipping tenant create as it already exists')
    else:
      errorInProcess("Error")
      
  tenantDICT, res = callGetService(ADMIN, "/" + masterTenantName + "/tenants/" + creationDICT['Name'], [200])
  if len(tenantDICT["AuthProviders"]) == 0:
    addAuthProvDICT = copy.deepcopy(tenantDICT)
    addAuthProvDICT["AuthProviders"].append(authProvCreationDICT)
    tenantDICT, res = callPutService(ADMIN, "/" + masterTenantName + "/tenants/" + creationDICT['Name'], addAuthProvDICT, [200])
    
  for curUser in range(10):
    print(" - user ", curUser)
    creationDICT = copy.deepcopy(registeruserDICT)
    creationDICT['authProviderGUID'] = tenantDICT["AuthProviders"][0]['guid']
    creationDICT['credentialJSON']['username'] = creationDICT['credentialJSON']['username'] + "T" + str(cur) + "_" + str(curUser)
    creationDICT['credentialJSON']['password'] = getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(env['APIAPP_DEFAULTHOMEADMINUSERNAME'], env['APIAPP_DEFAULTHOMEADMINPASSWORD'], tenantDICT["AuthProviders"][0]['saltForPasswordHashing'])
    resDICT, res = callPutService(LOGIN, "/" + tenantDICT['Name'] + "/register", creationDICT,[201,400])
    if (res==400):
      if (resDICT['message'] == 'That username is already in use'):
        print('Ignoring user create error as it already exists')
      else:
        errorInProcess("Error")
    

print("Creating more tenants without any users or auths")
for cur in range(15):
  print("Allow User Tenant ", cur)
  creationDICT = copy.deepcopy(tenantCreationDICT)
  creationDICT['Name'] = creationDICT['Name'] + "_nouser_" + str(cur)
  resDICT, res = callPostService(ADMIN, "/" + masterTenantName + "/tenants", creationDICT,[201, 400])
  if (res==400):
    if (resDICT['message'] == 'Tenant Already Exists'):
      print('Skipping tenant create as it already exists')
    else:
      errorInProcess("Error")

print("Creating teat tenant with internal and google auth")
creationDICT = copy.deepcopy(tenantCreationDICT)
creationDICT['Name'] = creationDICT['Name'] + "_googleAuthWithInternal"
resDICT, res = callPostService(ADMIN, "/" + masterTenantName + "/tenants", creationDICT,[201, 400])
if (res==400):
  if (resDICT['message'] == 'Tenant Already Exists'):
    print('Skipping tenant create as it already exists')
  else:
    print(resDICT)
    errorInProcess("Error")
else:
  addAuthProvider(creationDICT['Name'], authProvCreationDICT)
  addAuthProvider(creationDICT['Name'], authProvGoogleCreationDICT)

print("End")

#/public/login/{tenant}/authproviders

