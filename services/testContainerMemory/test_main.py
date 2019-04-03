#Script to test a running container
import unittest
import requests
import os
import json

baseURL="http://saas_user_management_system:80"
if ('BASEURL_TO_TEST' in os.environ):
  baseURL=os.environ['BASEURL_TO_TEST']

class test_containerAPI(unittest.TestCase):
#Actual tests below

  def test_WeCanGetToSwaggerFile(self):
    result = requests.get(baseURL + "/api/swagger.json")
    self.assertEqual(result.status_code, 200, msg="Wrong status code recieved from " + baseURL + "/api/swagger.json")

  def test_ContainerVersionMatchesEnviromentVariable(self):
    self.assertTrue('EXPECTED_CONTAINER_VERSION' in os.environ, msg="EXPECTED_CONTAINER_VERSION missing from enviroment")
    result = requests.get(baseURL + "/api/public/login/serverinfo")
    self.assertEqual(result.status_code, 200, msg="Wrong status code recieved from " + baseURL + "/api/public/login/serverinfo")
    resultJSON = json.loads(result.text)
    self.assertEqual(resultJSON['Server']['Version'], os.environ['EXPECTED_CONTAINER_VERSION'])
