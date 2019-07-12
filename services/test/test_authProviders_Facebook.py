from TestHelperSuperClass import httpOrigin, testHelperAPIClient, tenantWithNoAuthProviders, sampleInternalAuthProv001_CREATE_WithAllowUserCreation
import os
import copy
import constants
import json
from unittest.mock import patch, mock_open
from authProviders import authProviderFactory
from appObj import appObj


client_cliental_json_filename = 'facebookauth_client_public.json'


facebookAuthProv001_CREATE = {
  "guid": None,
  "Type": "facebook",
  "AllowUserCreation": False,
  "AllowLink": False,
  "AllowUnlink": False,
  "LinkText": 'Link',
  "MenuText": "Log in with Facebiij",
  "IconLink": "string",
  "ConfigJSON": "{\"clientSecretJSONFile\": \"" + os.path.dirname(os.path.realpath(__file__)) + "/../" + client_cliental_json_filename + "\"}",
  "saltForPasswordHashing": None
}
facebookAuthProv001_CREATE_withAllowCreate = copy.deepcopy(facebookAuthProv001_CREATE)
facebookAuthProv001_CREATE_withAllowCreate['AllowUserCreation'] = True

facebookAuthProv001_CREATE_missingClientSecretParam = copy.deepcopy(facebookAuthProv001_CREATE)
facebookAuthProv001_CREATE_missingClientSecretParam['ConfigJSON'] = "{}"
facebookAuthProv001_CREATE_badSecretFileParam = copy.deepcopy(facebookAuthProv001_CREATE)
facebookAuthProv001_CREATE_badSecretFileParam['ConfigJSON'] = "{\"clientSecretJSONFile\": \"badNonExistantFile.json\"}"


# Return values to be patched in to mock to simulate
#  facebooks response
#  mutiple to represent different logins
facebookLoginAccounts = []
facebookLoginAccounts.append({
})

class facebook_auth_test_api_helper_functions(testHelperAPIClient):
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

  def setupFacebookAuthOnMainTenantForTests(self, override_JSON = facebookAuthProv001_CREATE, tenantName = constants.masterTenantName):
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

  def loginWithFacebook(self, accNum, tenantName, authProviderDICT, expectedResults):
    loginJSON = {
      "credentialJSON":{
        "code":"4/RAHaPqLEg_L2qv2Xw0iutaKfDgqXcfV6ji_C4YoweqfakHy2PLbE9_p1DK2TuwSU839sVlcJ0yu0ThKyVOcToZU"
      },
      "authProviderGUID":authProviderDICT['guid']
    }
    result2 = None
    with patch("authProviders_Facebook.authProviderFacebook._enrichCredentialDictForAuth", return_value=facebookLoginAccounts[accNum]) as mock_loadStaticData:
      result2 = self.testClient.post(
        self.loginAPIPrefix + '/' + tenantName + '/authproviders',
        data=json.dumps(loginJSON),
        content_type='application/json',
        headers={"Origin": httpOrigin}
      )

    for x in expectedResults:
      if x == result2.status_code:
        return json.loads(result2.get_data(as_text=True))
    self.assertFalse(True, msg="Login status_code was " + str(result2.status_code) + " expected one of " + str(expectedResults))
    return None


class test_api(facebook_auth_test_api_helper_functions):

  def test_createAuth(self):
    resultJSON2 = self.setupFacebookAuthOnMainTenantForTests()

    expectedResult = copy.deepcopy(facebookAuthProv001_CREATE)
    expectedResult["StaticlyLoadedData"] = {"client_id": "FB_APP_ID"}

    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON2["AuthProviders"][1], expectedResult, ["guid","saltForPasswordHashing","StaticlyLoadedData"], msg='JSON of facebook Auth provider not right')
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON2["AuthProviders"][1]["StaticlyLoadedData"], expectedResult["StaticlyLoadedData"], ["client_id"], msg='StaticallyLoadedData Mismatch')

    result = self.testClient.get(self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants', headers={ constants.jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

    tenantJSON = copy.deepcopy(resultJSON['result'][0])
    tenantJSON['AuthProviders'].append(copy.deepcopy(facebookAuthProv001_CREATE_missingClientSecretParam))
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
    tenantJSON['AuthProviders'].append(copy.deepcopy(facebookAuthProv001_CREATE_badSecretFileParam))
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

    tenantDICT = self.addAuthProvider(resultJSON['result'][0], facebookAuthProv001_CREATE)
    googleAuthProv = tenantDICT['AuthProviders'][1]
    googleAuthProv['ConfigJSON'] = json.loads(googleAuthProv['ConfigJSON'])

    #Get Tenant will call auth provider for the first time
    #resetStaticData() #uncommenting this line should cause this test to error since the static data will be loaded from file
    with patch("authProviders_Facebook.loadStaticData", return_value={'web':{'client_id':'DummyClientID'}}) as mock_loadStaticData:
      a = authProviderFactory(googleAuthProv, googleAuthProv['guid'], constants.masterTenantName, None, appObj)
      if a==None:
        self.assertTrue(False, msg="authProviderFactory didn't create object")

    mock_loadStaticData.assert_not_called()


  def test_authFailsWithNoAuthsAccepted(self):
    #Test authentication via.
    ## Must use mocks

    resultJSON2 = self.setupFacebookAuthOnMainTenantForTests()
    googleAuthProvider = resultJSON2["AuthProviders"][1]

    result2JSON = self.loginWithFacebook(0, constants.masterTenantName, googleAuthProvider, [401])


  def test_authWithUserCreation(self):
    #Test authentication via google.
    ## Must use mocks
    tenantDict = self.createTenantWithAuthProvider(tenantWithNoAuthProviders, True, sampleInternalAuthProv001_CREATE_WithAllowUserCreation)

    resultJSON2 = self.setupFacebookAuthOnMainTenantForTests(facebookAuthProv001_CREATE_withAllowCreate, tenantDict['Name'])
    facebookAuthProvider = resultJSON2["AuthProviders"][1]

    result2JSON = self.loginWithFacebook(0, tenantDict['Name'], facebookAuthProvider, [200])

    #Turn off auto user creation
    tenantDict2 = self.getTenantDICT(tenantDict['Name'])
    tenantDict2['AllowUserCreation'] = False
    tenantDict3 = self.updateTenant(tenantDict2, [200])

    #Try and login - should not need to create so will suceed
    result3JSON = self.loginWithFacebook(0, tenantDict['Name'], facebookAuthProvider, [200])

  #Test user with google auth in one tenant can't log into a tenant they don't have access too
'''  def test_CrossTenantLoginsDisallowed(self):
    #Second tenant has allow user creation set to FALSE for this test to work - otherwise account is just auto created
    tenantWhereUserHasAccountDict = self.createTenantWithAuthProvider(tenantWithNoAuthProviders, True, googleAuthProv001_CREATE_withAllowCreate)
    tenantWithNoAuthProviders2 = copy.deepcopy(tenantWithNoAuthProviders)
    tenantWithNoAuthProviders2['Name'] = 'secondTestTenant'
    tenantWhereUserHasNoAccountDict = self.createTenantWithAuthProvider(tenantWithNoAuthProviders2, False, googleAuthProv001_CREATE_withAllowCreate)

    #Login as user on tenant where they have an account - this will cause the account to be autocreated
    result2JSON = self.loginWithFacebook(0, tenantWhereUserHasAccountDict['Name'], self.getTenantSpercificAuthProvDict(tenantWhereUserHasAccountDict['Name'], 'google'), [200])

    #Login as user on tenant where they have an account and ensure success
    result2JSON = self.loginWithFacebook(0, tenantWhereUserHasAccountDict['Name'], self.getTenantSpercificAuthProvDict(tenantWhereUserHasAccountDict['Name'], 'google'), [200])

    #Login as user on tenant where they have an account and ensure failure (no autocreation will occur)
    result2JSON = self.loginWithGoogle(0, tenantWhereUserHasNoAccountDict['Name'], self.getTenantSpercificAuthProvDict(tenantWhereUserHasNoAccountDict['Name'], 'google'), [401])


  #Test user with google auth creates a new account on second tenant the same user record is returned
  def test_AutocreateingGoogleAccountsInDifferentTenantsShareSameUser(self):
    tenant1 = self.createTenantWithAuthProvider(copy.deepcopy(tenantWithNoAuthProviders), True, copy.deepcopy(googleAuthProv001_CREATE_withAllowCreate))
    tenant2D = copy.deepcopy(tenantWithNoAuthProviders)
    tenant2D['Name'] = 'secondTestTenant'
    tenant2 = self.createTenantWithAuthProvider(tenant2D, True, copy.deepcopy(googleAuthProv001_CREATE_withAllowCreate))

    result2JSON = self.loginWithFacebook(0, tenant1['Name'], self.getTenantSpercificAuthProvDict(tenant1['Name'], 'google'), [200])

    result3JSON = self.loginWithFacebook(0, tenant2['Name'], self.getTenantSpercificAuthProvDict(tenant2['Name'], 'google'), [200])

    self.assertEqual(result2JSON['userGuid'],result3JSON['userGuid'],msg="Different user accounts returned")
    self.assertEqual(result2JSON['authedPersonGuid'],result3JSON['authedPersonGuid'],msg="Different person accounts used")

  def test_TwoUsersGetDifferentUserAndPersonIDs(self):
    tenant1 = self.createTenantWithAuthProvider(tenantWithNoAuthProviders, True, googleAuthProv001_CREATE_withAllowCreate)

    acc1LoginJSON = self.loginWithFacebook(0, tenant1['Name'], self.getTenantSpercificAuthProvDict(tenant1['Name'], 'google'), [200])
    acc2LoginJSON = self.loginWithFacebook(1, tenant1['Name'], self.getTenantSpercificAuthProvDict(tenant1['Name'], 'google'), [200])

    self.assertNotEqual(acc1LoginJSON['userGuid'],acc2LoginJSON['userGuid'],msg="user accounts returned should not be the same")
    self.assertNotEqual(acc1LoginJSON['authedPersonGuid'],acc2LoginJSON['authedPersonGuid'],msg="person accounts used should not be the same")
  '''
