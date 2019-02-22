#Python script to insert test data to a running instance
from constants import masterTenantName, jwtHeaderName
import requests
import json
import os
import bcrypt
from base64 import b64decode
import copy


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

def callService(api, url, method, dataDICT, expectedResponse):
  result = None
  targetURL = BASE[api] + url
  headers = {}
  if loginDICT is not None:
    #print(loginDICT['jwtData']['JWTToken'])
    headers[jwtHeaderName] = loginDICT['jwtData']['JWTToken']
  if method=='get':
    result = requests.get(
      targetURL
    )
  if method=='post':
    headers['content-type'] = 'application/json'
    result = requests.post(
      targetURL,
      data=json.dumps(dataDICT),
      headers=headers
    )
  if method=='put':
    headers['content-type'] = 'application/json'
    result = requests.put(
      targetURL,
      data=json.dumps(dataDICT),
      headers=headers
    )
  if result.status_code != expectedResponse:
    print("Sending " + method + " to ", targetURL)
    if dataDICT is not None:
      print(" data:", dataDICT)
    print("Got response ",result.status_code)
    print("     ",result.text)
    raise Exception("Did not get expected response")
  return json.loads(result.text)
  
  
def callGETService(api,url, expectedResponse):
  return callService(api,url, "get", None, expectedResponse)

def callpostService(api,url, POSTdict, expectedResponse):
  return callService(api,url, "post", POSTdict, expectedResponse)

def callputService(api,url, PUTdict, expectedResponse):
  return callService(api,url, "put", PUTdict, expectedResponse)

print("Start of script to insert test data")

AuthProvidersDICT = callGETService(LOGIN, "/" + masterTenantName + "/authproviders", 200)
MainAuthProvider = AuthProvidersDICT['AuthProviders'][0]

loginCallDICT = {
  "authProviderGUID": MainAuthProvider['guid'],
  "credentialJSON": { 
    "username": env['APIAPP_DEFAULTHOMEADMINUSERNAME'], 
    "password": getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(env['APIAPP_DEFAULTHOMEADMINUSERNAME'], env['APIAPP_DEFAULTHOMEADMINPASSWORD'], MainAuthProvider['saltForPasswordHashing'])
   }
}
loginDICT = callpostService(LOGIN, "/" + masterTenantName + "/authproviders",loginCallDICT,200)

tenantCreationDICT = {
  "Name": "testData_Tenant",
  "Description": "Created by insert_test_data.py",
  "AllowUserCreation": True,
  "AuthProviders": [{
    "guid": None,
    "Type": "internal",
    "AllowUserCreation": True,
    "MenuText": "Default Menu Text",
    "IconLink": "string",
    "ConfigJSON": "{\"userSufix\": \"@testUserSufix\"}",
    "saltForPasswordHashing": None
  }]
}

CreatedTenants = []
for cur in range(4):
  creationDICT = copy.deepcopy(tenantCreationDICT)
  creationDICT['Name'] = creationDICT['Name'] + str(cur)
  CreatedTenants.append(callpostService(ADMIN, "/" + masterTenantName + "/tenants", creationDICT,201))


print("End")

#/public/login/{tenant}/authproviders

