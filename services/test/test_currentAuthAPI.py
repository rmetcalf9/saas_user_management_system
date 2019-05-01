from TestHelperSuperClass import testHelperAPIClient
from constants import masterTenantName, jwtHeaderName, jwtCookieName, DefaultHasAccountRole, masterTenantDefaultSystemAdminRole, objectVersionHeaderName
import json
import copy
from tenants import CreatePerson, GetTenant, _getAuthProvider
from appObj import appObj
from authProviders import authProviderFactory
from authProviders_base import getAuthRecord



class test_securityTests(testHelperAPIClient):
  def test_get_currentAuthInfo_noAccessWithoutHeader(self):
    result = self.testClient.get(self.currentAuthAPIPrefix + '/' + masterTenantName + '/currentAuthInfo', headers={})
    self.assertEqual(result.status_code, 401, msg='noAccess Test failed - ' + result.get_data(as_text=True))


  def test_get_currentAuthInfo_forDefaultUser(self): 
    result = self.testClient.get(self.currentAuthAPIPrefix + '/' + masterTenantName + '/currentAuthInfo', headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

    expectedPersonResult = {
      "ObjectVersion": "1", 
      "associatedUsers": [{
        "ObjectVersion": "4", 
        "TenantRoles": [{"TenantName": "usersystem", "ThisTenantRoles": ["hasaccount", "securityTest", "systemadmin"]}], 
        "UserID": "FORCED-CONSTANT-TESTING-GUID", 
        "associatedPersonGUIDs": ["FORCED-CONSTANT-TESTING-PERSON-GUID"], 
        "creationDateTime": "2019-04-30T09:03:35.241658+00:00", 
        "known_as": "AdminTestSet", 
        "lastUpdateDateTime": "2019-04-30T09:03:35.241718+00:00", 
        "other_data": {"createdBy": "init/CreateMasterTenant"}
      }], 
      "creationDateTime": "2019-04-30T09:03:35.241723+00:00", 
      "guid": "FORCED-CONSTANT-TESTING-PERSON-GUID", 
      "lastUpdateDateTime": "2019-04-30T09:03:35.241723+00:00", 
      "personAuths": [{
        "AuthProviderGUID": "9a649f23-e8b4-42ba-b613-9bac7911980b", 
        "AuthProviderType": "internal", 
        "AuthUserKey": "AdminTestSet@internalDataStore_`@\\/'internal", 
        "known_as": "AdminTestSet", 
        "tenantName": "usersystem"
       }]
    }
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON["loggedInPerson"], expectedPersonResult, ["associatedUsers", "personAuths", "creationDateTime", "lastUpdateDateTime"], msg='Did not get expected Person result')
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON["loggedInPerson"]["associatedUsers"][0], expectedPersonResult["associatedUsers"][0], ["creationDateTime", "lastUpdateDateTime"], msg='Did not get expected Person->associatedUsers result')
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON["loggedInPerson"]["personAuths"][0], expectedPersonResult["personAuths"][0], ["AuthProviderGUID"], msg='Did not get expected Person->personAuths result')
    
    
    expectedUserResult = {
      "ObjectVersion": "4", 
      "TenantRoles": [{"TenantName": "usersystem", "ThisTenantRoles": ["hasaccount", "securityTest", "systemadmin"]}], 
      "UserID": "FORCED-CONSTANT-TESTING-GUID", 
      "associatedPersonGUIDs": ["FORCED-CONSTANT-TESTING-PERSON-GUID"], 
      "creationDateTime": "2019-04-30T09:09:37.156689+00:00", 
      "known_as": "AdminTestSet", 
      "lastUpdateDateTime": "2019-04-30T09:09:37.156709+00:00", 
      "other_data": {"createdBy": "init/CreateMasterTenant"}
    }
    
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON["loggedInUser"], expectedUserResult, ["creationDateTime", "lastUpdateDateTime"], msg='Did not get expected User result')
    
