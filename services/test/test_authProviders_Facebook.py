from TestHelperSuperClass import httpOrigin, testHelperAPIClient, tenantWithNoAuthProviders, sampleInternalAuthProv001_CREATE_WithAllowUserCreation
import os
import copy
import constants
import json

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


class test_api(facebook_auth_test_api_helper_functions):


  def test_createAuth(self):
    resultJSON2 = self.setupFacebookAuthOnMainTenantForTests()

    expectedResult = copy.deepcopy(facebookAuthProv001_CREATE)
    expectedResult["StaticlyLoadedData"] = {"client_id": "FB_APP_ID"}

    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON2["AuthProviders"][1], expectedResult, ["guid","saltForPasswordHashing","StaticlyLoadedData"], msg='JSON of facebook Auth provider not right')
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON2["AuthProviders"][1]["StaticlyLoadedData"], expectedResult["StaticlyLoadedData"], ["client_id"], msg='StaticallyLoadedData Mismatch')
