from TestHelperSuperClass import testHelperAPIClient, tenantWithNoAuthProviders
from appObj import appObj
from tenants import GetTenant
import constants
import json
import copy
import os
from authProviders import authProviderFactory
from unittest.mock import patch, mock_open
from authProviders_base import resetStaticData


#client_cliental_json_filename = 'googleauth_client_public.json'
client_cliental_json_filename = 'googleauth_client_secret.json'

googleAuthProv001_CREATE = {
  "guid": None,
  "Type": "google",
  "AllowUserCreation": False,
  "MenuText": "Log in with Google",
  "IconLink": "string",
  "ConfigJSON": "{\"clientSecretJSONFile\": \"" + os.path.dirname(os.path.realpath(__file__)) + "/../" + client_cliental_json_filename + "\"}",
  "saltForPasswordHashing": None
}

exampleEnrichedCredentialJSON = {
  "code": "AAA",
  "creds": {
    "access_token": "XXX", 
    "client_id": "XXX", 
    "client_secret": "XXX", 
    "refresh_token": "XXX", 
    "token_expiry": "2019-05-08T14:55:14Z", 
    "token_uri": "https://oauth2.googleapis.com/token", 
    "user_agent": None, 
    "revoke_uri": "https://oauth2.googleapis.com/revoke", 
    "id_token": {
      "iss": "https://accounts.google.com", 
      "azp": "???.apps.googleusercontent.com", 
      "aud": "???.apps.googleusercontent.com", 
      "sub": "56454656465454", 
      "email": "rmetcalf9@googlemail.com", 
      "email_verified": True, 
      "at_hash": "???", 
      "name": "Robert Metcalf", 
      "picture": "https://lh6.googleusercontent.com/dsaddsaffs/s96-c/photo.jpg", 
      "given_name": "Robert", 
      "family_name": "Metcalf", 
      "locale": "en-GB", 
      "iat": 342543, 
      "exp": 324324
    }, 
  }
}

googleAuthProv001_CREATE_missingClientSecretParam = copy.deepcopy(googleAuthProv001_CREATE)
googleAuthProv001_CREATE_missingClientSecretParam['ConfigJSON'] = "{}"
googleAuthProv001_CREATE_badSecretFileParam = copy.deepcopy(googleAuthProv001_CREATE)
googleAuthProv001_CREATE_badSecretFileParam['ConfigJSON'] = "{\"clientSecretJSONFile\": \"badNonExistantFile.json\"}"

class test_api(testHelperAPIClient):
  def addAuthProvider(self, currentTenantJSON, authProviderDICT):
    tenantJSON = copy.deepcopy(currentTenantJSON)
    tenantJSON['AuthProviders'].append(copy.deepcopy(authProviderDICT))
    tenantJSON['ObjectVersion'] = currentTenantJSON['ObjectVersion']
    result = self.testClient.put(
      self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants/' + tenantJSON['Name'], 
      headers={ constants.jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantJSON), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 200, msg="Failed to add auth - " + result.get_data(as_text=True))
    return json.loads(result.get_data(as_text=True))
  
  def setupGoogleAuthOnMainTenantForTests(self, override_JSON = googleAuthProv001_CREATE, tenantName = constants.masterTenantName):
    result = self.testClient.get(self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants', headers={ constants.jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))
    for x in resultJSON['result']:
      if x['Name'] == tenantName:
        self.addAuthProvider(x, override_JSON)
    
    result2 = self.testClient.get(self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants', headers={ constants.jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result2.status_code, 200)
    resultJSON2 = json.loads(result2.get_data(as_text=True))
    for x in resultJSON2['result']:
      if x['Name'] == tenantName:
        return x
    return None
  
class test_addGoogleAuthProviderToMasterTenant(test_api):    
  def test_createAuth(self):
    resultJSON2 = self.setupGoogleAuthOnMainTenantForTests()
    
    expectedResult = copy.deepcopy(googleAuthProv001_CREATE)
    expectedResult["StaticlyLoadedData"] = {"client_id": "someGoogleID.apps.googleusercontent.com"}

    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON2["AuthProviders"][1], expectedResult, ["guid","saltForPasswordHashing","StaticlyLoadedData"], msg='JSON of google Auth provider not right')
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON2["AuthProviders"][1]["StaticlyLoadedData"], expectedResult["StaticlyLoadedData"], ["client_id"], msg='StaticallyLoadedData Mismatch')
    if not resultJSON2["AuthProviders"][1]["StaticlyLoadedData"]["client_id"].endswith(".apps.googleusercontent.com"):
      self.assertFalse(True,msg="Invalid Client ID")

  def test_createAuthMissingclientSecretJSONFileParam(self):
    result = self.testClient.get(self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants', headers={ constants.jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

    tenantJSON = copy.deepcopy(resultJSON['result'][0])
    tenantJSON['AuthProviders'].append(copy.deepcopy(googleAuthProv001_CREATE_missingClientSecretParam))
    tenantJSON['ObjectVersion'] = resultJSON['result'][0]['ObjectVersion']
    result = self.testClient.put(
      self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants/' + tenantJSON['Name'], 
      headers={ constants.jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantJSON), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg='Create should have failed')

  
  def test_createAuthMissingclientSecretJSONFile(self):
    result = self.testClient.get(self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants', headers={ constants.jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

    tenantJSON = copy.deepcopy(resultJSON['result'][0])
    tenantJSON['AuthProviders'].append(copy.deepcopy(googleAuthProv001_CREATE_badSecretFileParam))
    tenantJSON['ObjectVersion'] = resultJSON['result'][0]['ObjectVersion']
    result = self.testClient.put(
      self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants/' + tenantJSON['Name'], 
      headers={ constants.jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantJSON), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg='Create should have failed')

  def test_authProviderObjectOnlyReadsFromFileOnce(self):
    result = self.testClient.get(self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants', headers={ constants.jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

    tenantDICT = self.addAuthProvider(resultJSON['result'][0], googleAuthProv001_CREATE)
    googleAuthProv = tenantDICT['AuthProviders'][1]
    googleAuthProv['ConfigJSON'] = json.loads(googleAuthProv['ConfigJSON'])
    
    #Get Tenant will call auth provider for the first time
    #resetStaticData() #uncommenting this line should cause this test to error since the static data will be loaded from file
    with patch("authProviders_Google.loadStaticData", return_value={'web':{'client_id':'DummyClientID'}}) as mock_loadStaticData:
      a = authProviderFactory(googleAuthProv, googleAuthProv['guid'], constants.masterTenantName, None)
      if a==None:
        self.assertTrue(False, msg="authProviderFactory didn't create object")
    
    mock_loadStaticData.assert_not_called()
    
  def test_authFailsWithNoGoogleAuthsAccepted(self):
    #Test authentication via google.
    ## Must use mocks
    
    resultJSON2 = self.setupGoogleAuthOnMainTenantForTests()
    googleAuthProvider = resultJSON2["AuthProviders"][1]
    
    loginJSON = {
      "credentialJSON":{
        "code":"4/RAHaPqLEg_L2qv2Xw0iutaKfDgqXcfV6ji_C4YoweqfakHy2PLbE9_p1DK2TuwSU839sVlcJ0yu0ThKyVOcToZU"
      },
      "authProviderGUID":googleAuthProvider['guid']
    }
    result2 = None
    with patch("authProviders_Google.authProviderGoogle._enrichCredentialDictForAuth", return_value=exampleEnrichedCredentialJSON) as mock_loadStaticData:
      result2 = self.testClient.post(self.loginAPIPrefix + '/' + constants.masterTenantName + '/authproviders', data=json.dumps(loginJSON), content_type='application/json')
      self.assertEqual(result2.status_code, 401)
      result2JSON = json.loads(result2.get_data(as_text=True))

  def test_authWithUserCreation(self):
    #Test authentication via google.
    ## Must use mocks
    tenantDict = self.setupTenantForTesting(tenantWithNoAuthProviders, False, True)

    googleAuthProv001_CREATE_withAllowCreate = copy.deepcopy(googleAuthProv001_CREATE)
    googleAuthProv001_CREATE_withAllowCreate['AllowUserCreation'] = True
    resultJSON2 = self.setupGoogleAuthOnMainTenantForTests(googleAuthProv001_CREATE_withAllowCreate, tenantDict['Name'])
    googleAuthProvider = resultJSON2["AuthProviders"][1]
    
    loginJSON = {
      "credentialJSON":{
        "code":"4/RAHaPqLEg_L2qv2Xw0iutaKfDgqXcfV6ji_C4YoweqfakHy2PLbE9_p1DK2TuwSU839sVlcJ0yu0ThKyVOcToZU"
      },
      "authProviderGUID":googleAuthProvider['guid']
    }
    result2 = None
    with patch("authProviders_Google.authProviderGoogle._enrichCredentialDictForAuth", return_value=exampleEnrichedCredentialJSON) as mock_loadStaticData:
      result2 = self.testClient.post(self.loginAPIPrefix + '/' + tenantDict['Name'] + '/authproviders', data=json.dumps(loginJSON), content_type='application/json')
      self.assertEqual(result2.status_code, 200, msg="recieved " + result2.get_data(as_text=True))
      result2JSON = json.loads(result2.get_data(as_text=True))

    self.assertTrue(False, msg="TODO Check user exists in system")

