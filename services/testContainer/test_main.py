#Script to test a running container
import unittest
import requests
import os
import json

baseURL="http://saas_user_management_system:8098"
if ('BASEURL_TO_TEST' in os.environ):
  baseURL=os.environ['BASEURL_TO_TEST']

class test_containerAPI(unittest.TestCase):
#Actual tests below

  def test_WeCanGetToSwaggerFile(self):
    result = requests.get(baseURL + "/api/swagger.json")
    self.assertEqual(result.status_code, 200)

  def test_ContainerVersionMatchesEnviromentVariable(self):
    self.assertTrue('EXPECTED_CONTAINER_VERSION' in os.environ)
    result = requests.get(baseURL + "/api/serverinfo/")
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.text)
    self.assertEqual(resultJSON['Server']['Version'], os.environ['EXPECTED_CONTAINER_VERSION'])
