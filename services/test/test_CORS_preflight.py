'''
Test the preflight options return values are correct
'''
from TestHelperSuperClass import tenantWithNoAuthProviders, env, httpOrigin, testHelperAPIClient
import constants
import json
import copy

#Origin can only have one value
## http://blog.crashtest-security.com/multiple-values-access-control-allow-origin

class corsPreflight_helpers(testHelperAPIClient):
  def findCORSReturnVals(self, tenantName, origin):
    loginJSON = {}
    result2 = self.testClient.options(
      self.loginAPIPrefix + '/' + tenantName + '/authproviders',
      data=json.dumps(loginJSON), content_type='application/json',
      headers={"Origin": origin}
    )
    self.assertEqual(result2.status_code, 200, msg="Options request did not return 200")
    return result2.headers

class test_corsPreflight(corsPreflight_helpers):
  def test_simpleCorsCall(self):
    a = self.findCORSReturnVals(constants.masterTenantName, httpOrigin)

    self.assertEqual(a.get("Access-Control-Allow-Origin"),env["APIAPP_COMMON_ACCESSCONTROLALLOWORIGIN"])

#TODO Test for combinations of data
class test_corsPreflightHasMasterTenantHosts(corsPreflight_helpers):
  def test_twoTenantsCall(self):
    tenantWithDifferentAllowedOrigin = copy.deepcopy(tenantWithNoAuthProviders)
    tenantWithDifferentAllowedOrigin["JWTCollectionAllowedOriginList"] = ["http://h.com", "hyyp://i.com"]
    tenantJSON = self.createTenantForTesting(tenantWithDifferentAllowedOrigin)

    #Getting auth providers for a tennant should cause it's allowed origin entries to be included in cors corsPreflight_helpers
    result = self.testClient.get(
      self.loginAPIPrefix + '/' + tenantWithDifferentAllowedOrigin["Name"] + '/authproviders',
      #headers={"Origin": httpOrigin}
      headers=None #aet auth prov should not require an origin header
    )
    self.assertEqual(result.status_code, 200)

TODO Check for each valid origin and one invalid one
    a = self.findCORSReturnVals(constants.masterTenantName, httpOrigin)

    self.assertEqual(a.get("Access-Control-Allow-Origin"),env["APIAPP_COMMON_ACCESSCONTROLALLOWORIGIN"] + ", http://h.com, hyyp://i.com")
