from TestHelperSuperClass import testHelperAPIClient, env
import unittest
import json
from appObj import appObj
import pytz
import datetime

serverInfo = {
      'Server': {
        'Version': env['APIAPP_VERSION'],
        "APIAPP_APIDOCSURL": "_",
        "APIAPP_FRONTENDURL": env["APIAPP_FRONTENDURL"]
      }
}


class test_api(testHelperAPIClient):

  def test_getServerInfo(self):
    result = self.testClient.get(self.serverinfoAPIPrefix + '/serverinfo')
    self.assertEqual(result.status_code, 200, msg="Wrong response when calling " + self.serverinfoAPIPrefix + "/serverinfo")
    resultJSON = json.loads(result.get_data(as_text=True))
    self.assertJSONStringsEqual(resultJSON, serverInfo)

  def test_swaggerJSONProperlyShared(self):
    result = self.testClient.get('/api/swagger.json')
    self.assertEqual(result.status_code, 200)
    result = self.testClient.get('/apidocs/swagger.json')
    self.assertEqual(result.status_code, 200)
