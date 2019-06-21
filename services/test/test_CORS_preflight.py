'''
Test the preflight options return values are correct
'''
from TestHelperSuperClass import env, httpOrigin, testHelperAPIClient
import constants
import json


class corsPreflight_helpers(testHelperAPIClient):
  def findCORSReturnVals(self, tenantName):
    loginJSON = {}
    result2 = self.testClient.options(
      self.loginAPIPrefix + '/' + tenantName + '/authproviders',
      data=json.dumps(loginJSON), content_type='application/json',
      headers={"Origin": httpOrigin}
    )
    self.assertEqual(result2.status_code, 200, msg="Options request did not return 200")
    return result2.headers

class test_corsPreflight(corsPreflight_helpers):
  def test_simpleCorsCall(self):
    a = self.findCORSReturnVals(constants.masterTenantName)

    self.assertEqual(a.get("Access-Control-Allow-Origin"),env["APIAPP_COMMON_ACCESSCONTROLALLOWORIGIN"])

#TODO Test for combinations of data
#class test_corsPreflightHasMasterTenantHosts(corsPreflight_helpers):
#  def test_simpleCorsCall(self):
#    a = self.findCORSReturnVals(constants.masterTenantName)
#    print(a)
#
#    self.assertEqual(a.get("Access-Control-Allow-Origin"),env["APIAPP_COMMON_ACCESSCONTROLALLOWORIGIN"])
