from datetime import datetime, timedelta
import pytz
from TestHelperSuperClass import testHelperAPIClient, env
from appObj import appObj
from constants import masterTenantName, jwtHeaderName
from test_adminAPI import test_api as parent_test_api
import json

#Test user functoins of the admin API

class test_adminAPIUsers(parent_test_api):
  def test_getDefaultListFromMasterTenant(self):
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/users', headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    
    resultJSON = json.loads(result.get_data(as_text=True))
    self.assertEqual(resultJSON['pagination']['total'],1)
    
    expectedResult = {
      'UserID': 'FORCED-CONSTANT-TESTING-GUID',
      'known_as': env['APIAPP_DEFAULTHOMEADMINUSERNAME'],
      'other_data': {}
    }

    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON['result'][0],expectedResult, ["TenantRoles"], msg="User data mismatch")
    
    self.assertEqual(len(resultJSON['result'][0]["TenantRoles"]),1,msg="Didn't return single tenant")

    expectedTenantRolesResult = [{
      "TenantName": masterTenantName,
      "ThisTenantRoles": ['systemadmin', 'hasaccount']
    }]
    
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON['result'][0]["TenantRoles"],expectedTenantRolesResult, ["TenantRoles"], msg="Tenant Roles returned data wrong")
    
    
   

