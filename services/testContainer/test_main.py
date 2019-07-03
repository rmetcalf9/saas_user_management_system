#Script to test a running container
import unittest
import os
import json
from containerTestCommon import httpOrigin, baseURL, callGetService, callPutService
import containerTestCommon
import copy_of_main_constants_do_not_edit as constants

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

  def test_putCall(self):
    #With nginx not sure if put call will work.
    # if we get 503 we are getting an nginx error
    PUTdict = { "invalid": True }
    loginDICT = containerTestCommon.getLoginDICTForDefaultUser(self)
    jwtToken = loginDICT['jwtData']['JWTToken']

    headers = {"Authorization": "Bearer " + jwtToken, "Origin": httpOrigin}
    cookies = {}

    callPutService(containerTestCommon.ADMINFRONTEND,"/" + constants.masterTenantName + "/tenants/usersystem", PUTdict, [405], loginDICT, headers, cookies)

  def test_URLParamsGoToServer(self):
    if containerTestCommon.runningViaKong:
      print("Skipping test_testNormalJWTHeader as this won't work via Kong - Kong can not read custom headers")
      return

    #https://api.metcarob.com/saas_user_management/v0/authed/api/admin/usersystem/users?query=code&pagesize=100&offset=0
    loginDICT = containerTestCommon.getLoginDICTForDefaultUser(self)
    jwtToken = loginDICT['jwtData']['JWTToken']
    headers = {}
    cookies = {constants.jwtCookieName: jwtToken}
    res, _ = callGetService(
      containerTestCommon.ADMIN,
      "/" + constants.masterTenantName + "/users",
      [200],
      None,
      headers,
      cookies
    )
    self.assertNotEqual(len(res['result']), 0, msg="Should not have zero users")
    res2, _ = callGetService(
      containerTestCommon.ADMIN,
      "/" + constants.masterTenantName + "/users?query=codedfskhdsgew43tgrsadsasd&pagesize=100&offset=0&someotherparam=abs",
      [200],
      None,
      headers,
      cookies
    )
    print(res2)
    self.assertEqual(len(res2['result']), 0, msg="Query paramater should have resulted in no results")
