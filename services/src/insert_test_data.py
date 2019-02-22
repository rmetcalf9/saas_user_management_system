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

def callService(api, url, method, dataDICT, expectedResponses):
  result = None
  targetURL = BASE[api] + url
  headers = {}
  if loginDICT is not None:
    #print(loginDICT['jwtData']['JWTToken'])
    headers[jwtHeaderName] = loginDICT['jwtData']['JWTToken']
  if method=='get':
    result = requests.get(
      targetURL,
      headers=headers
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
    "MenuText": "Default Menu Text",
    "IconLink": "string",
    "ConfigJSON": "{\"userSufix\": \"@testUserSufix\"}",
    "saltForPasswordHashing": None
}

registeruserDICT = {
  "authProviderGUID": "TODO",
  "credentialJSON": { 
    "username": "testUser_", 
    "password": getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(env['APIAPP_DEFAULTHOMEADMINUSERNAME'], env['APIAPP_DEFAULTHOMEADMINPASSWORD'], MainAuthProvider['saltForPasswordHashing'])
   }
}

print("Creating allowUserCreation tenants with users created with register method")
for cur in range(4):
  creationDICT = copy.deepcopy(tenantCreationDICT)
  creationDICT['Name'] = creationDICT['Name'] + str(cur)
  resDICT, res = callPostService(ADMIN, "/" + masterTenantName + "/tenants", creationDICT,[201, 400])
  if (res==400):
    if (resDICT['message'] == 'Tenant Already Exists'):
      print('Skipping tenant create as it already exists')
    else:
      raise Exception()
      
  tenantDICT, res = callGetService(ADMIN, "/" + masterTenantName + "/tenants/" + creationDICT['Name'], [200])
  if len(tenantDICT["AuthProviders"]) == 0:
    addAuthProvDICT = copy.deepcopy(tenantDICT)
    addAuthProvDICT["AuthProviders"].append(authProvCreationDICT)
    tenantDICT, res = callPutService(ADMIN, "/" + masterTenantName + "/tenants/" + creationDICT['Name'], addAuthProvDICT, [200])
    
  for curUser in range(10):
    creationDICT = copy.deepcopy(registeruserDICT)
    creationDICT['authProviderGUID'] = tenantDICT["AuthProviders"][0]['guid']
    creationDICT['credentialJSON']['username'] = creationDICT['credentialJSON']['username'] + "T" + str(cur) + "_" + str(curUser)
    creationDICT['credentialJSON']['password'] = getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(env['APIAPP_DEFAULTHOMEADMINUSERNAME'], env['APIAPP_DEFAULTHOMEADMINPASSWORD'], tenantDICT["AuthProviders"][0]['saltForPasswordHashing'])
    resDICT, res = callPutService(LOGIN, "/" + tenantDICT['Name'] + "/register", creationDICT,[201,400])
    if (res==400):
      if (resDICT['message'] == 'That username is already in use'):
        print('Ignoring user create error as it already exists')
      else:
        raise Exception()
    
  


print("End")

#/public/login/{tenant}/authproviders

