from TestHelperSuperClass import testHelperAPIClient, env
import unittest
import json
from appObj import appObj
import pytz
import datetime

invalidTenantName="invalidtenantname"

class test_api(testHelperAPIClient):

  def test_loginInvalidTenantFails(self):
    result = self.testClient.get('/api/login/' + invalidTenantName + '/authproviders')
    self.assertEqual(result.status_code, 400)
    resultJSON = json.loads(result.get_data(as_text=True))
    print(resultJSON)
    self.assertJSONStringsEqual(resultJSON, {"message": "Tenant not found"})



