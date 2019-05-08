from TestHelperSuperClass import testHelperAPIClient
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
  
  def setupGoogleAuthOnMainTenantForTests(self):
    result = self.testClient.get(self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants', headers={ constants.jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

    self.addAuthProvider(resultJSON['result'][0], googleAuthProv001_CREATE)
    
    result2 = self.testClient.get(self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants', headers={ constants.jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result2.status_code, 200)
    resultJSON2 = json.loads(result2.get_data(as_text=True))

    return resultJSON2
  
class test_addGoogleAuthProviderToMasterTenant(test_api):    
  def test_createAuth(self):
    resultJSON2 = self.setupGoogleAuthOnMainTenantForTests()
    
    expectedResult = copy.deepcopy(googleAuthProv001_CREATE)
    expectedResult["StaticlyLoadedData"] = {"client_id": "someGoogleID.apps.googleusercontent.com"}

    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON2["result"][0]["AuthProviders"][1], expectedResult, ["guid","saltForPasswordHashing","StaticlyLoadedData"], msg='JSON of google Auth provider not right')
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON2["result"][0]["AuthProviders"][1]["StaticlyLoadedData"], expectedResult["StaticlyLoadedData"], ["client_id"], msg='StaticallyLoadedData Mismatch')
    if not resultJSON2["result"][0]["AuthProviders"][1]["StaticlyLoadedData"]["client_id"].endswith(".apps.googleusercontent.com"):
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
    googleAuthProvider = resultJSON2["result"][0]["AuthProviders"][1]
    
    loginJSON = {
      "credentialJSON":{
        "code":"4/RAHaPqLEg_L2qv2Xw0iutaKfDgqXcfV6ji_C4YoweqfakHy2PLbE9_p1DK2TuwSU839sVlcJ0yu0ThKyVOcToZU"
      },
      "authProviderGUID":googleAuthProvider['guid']
    }
    result2 = self.testClient.post(self.loginAPIPrefix + '/' + constants.masterTenantName + '/authproviders', data=json.dumps(loginJSON), content_type='application/json')
    self.assertEqual(result2.status_code, 200)
    result2JSON = json.loads(result2.get_data(as_text=True))

    expectedResult = {
      "userGuid": "FORCED-CONSTANT-TESTING-GUID",
      "authedPersonGuid": "Ignore",
      "ThisTenantRoles": [masterTenantDefaultSystemAdminRole, DefaultHasAccountRole, constants.SecurityEndpointAccessRole],
      "known_as": env['APIAPP_DEFAULTHOMEADMINUSERNAME']
    }
    self.assertJSONStringsEqualWithIgnoredKeys(result2JSON, expectedResult, [ 'jwtData', 'authedPersonGuid', 'refresh' ])

