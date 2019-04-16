#Script to test a running container
import unittest
import os
import json
from containerTestCommon import baseURL, callGetService
import containerTestCommon

class test_containerAPI(unittest.TestCase):
#Actual tests below




  def test_WeCanGetToSwaggerFileForAPIDocs(self):
    callGetService(containerTestCommon.APIDOCS, "/swagger.json", [200], None, None, None)
  def test_WeCanGetToAPIDocsURL(self):
    callGetService(containerTestCommon.APIDOCS, "/", [200], None, None, None)

  def test_ContainerVersionMatchesEnviromentVariable(self):
    self.assertTrue('EXPECTED_CONTAINER_VERSION' in os.environ, msg="EXPECTED_CONTAINER_VERSION missing from enviroment")
    resultJSON, status = callGetService(containerTestCommon.LOGIN, "/serverinfo", [200], None, None, None)
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
    callGetService(containerTestCommon.APIDOCS, "/swaggerui/bower/swagger-ui/dist/droid-sans.css", [200], None, None, None)
    
  def test_adminfrontendMainPage(self):
    callGetService(containerTestCommon.ADMINFRONTEND, "/", [200], None, None, None)
    callGetService(containerTestCommon.ADMINFRONTEND, "/#/usersystem/", [200], None, None, None)

  def test_frontendMainPage(self):
    callGetService(containerTestCommon.FRONTEND, "/", [200], None, None, None) #This gives us Quasar 404 page but still a 200 response
    callGetService(containerTestCommon.FRONTEND, "/#/usersystem/", [200], None, None, None)
    
    