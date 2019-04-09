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
  def  callGetService(self, url, expectedResultList):
    result = requests.get(url)
    for a in expectedResultList:
      if result.status_code == a:
        return result
    self.assertFalse(True, msg="Got response " + str(result.status_code) + " from " + url + " expected one of " + str(expectedResultList))
    
    return result



  def test_WeCanGetToSwaggerFileForAPIDocs(self):
    self.callGetService(baseURL + "/public/web/apidocs/swagger.json", [200])
  def test_WeCanGetToAPIDocsURL(self):
    self.callGetService(baseURL + "/public/web/apidocs/", [200])

  def test_ContainerVersionMatchesEnviromentVariable(self):
    self.assertTrue('EXPECTED_CONTAINER_VERSION' in os.environ, msg="EXPECTED_CONTAINER_VERSION missing from enviroment")
    result = self.callGetService(baseURL + "/public/api/login/serverinfo", [200])
    resultJSON = json.loads(result.text)
    self.assertEqual(resultJSON['Server']['Version'], os.environ['EXPECTED_CONTAINER_VERSION'])

  #TODO Test apidocs url retrieved from serverinfo works
  #Test not valid - the returned url is an external url and requires Kong
  # this test only runs directly on the container
  #def test_CanAccessAPIDocsLocationReturnedByServerInfo(self):
  #  self.assertTrue('EXPECTED_CONTAINER_VERSION' in os.environ, msg="EXPECTED_CONTAINER_VERSION missing from enviroment")
  #  result = self.callGetService(baseURL + "/public/api/login/serverinfo", [200])
  #  print(result.text)
  #  resultJSON = json.loads(result.text)
  #  self.assertEqual(resultJSON['Server']['APIAPP_APIDOCSURL'], baseURL + "/public/web/apidocs")
    
  def test_WeCanGetToSwaggerUIStaticFiles(self):
    self.callGetService(baseURL + "/public/web/apidocs/swaggerui/bower/swagger-ui/dist/droid-sans.css", [200])
    
   
    