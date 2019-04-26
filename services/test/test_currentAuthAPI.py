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

    expectedResult = {
      'TODO': 'TODO'
    }
    
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON, expectedResult, [], msg='Did not get expected result')
    
