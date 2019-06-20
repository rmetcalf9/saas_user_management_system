#Script to test a running container
import unittest
import os
import json
from containerTestCommon import getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse, getEnviromentVariable, LOGIN, httpOrigin, baseURL, callGetService, callPostService, callPutService
import containerTestCommon
import copy_of_main_constants_do_not_edit as constants

class test_origin(unittest.TestCase):
#Actual tests below


  def testPOSTWithoutOriginFails(self):
    AuthProvidersDICT,res = callGetService(
      LOGIN, "/" + constants.masterTenantName + "/authproviders",
      [200],
      None,
      None,
      None
    )
    MainAuthProvider = AuthProvidersDICT['AuthProviders'][0]

    loginCallDICT = {
      "authProviderGUID": MainAuthProvider['guid'],
      "credentialJSON": {
        "username": getEnviromentVariable('APIAPP_DEFAULTHOMEADMINUSERNAME'),
        "password": getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(
          getEnviromentVariable('APIAPP_DEFAULTHOMEADMINUSERNAME'),
          getEnviromentVariable('APIAPP_DEFAULTHOMEADMINPASSWORD'),
          MainAuthProvider['saltForPasswordHashing']
        )
       }
    }
    ###print("Login DICT:",loginCallDICT)
    loginDICT,res = callPostService(
      LOGIN,
      "/" + constants.masterTenantName + "/authproviders",
      loginCallDICT,[401],
      None,
      None,
      None,
      addOrigin=False
    )
    self.assertEqual(loginDICT["message"], "Invalid Origin", msg="Wrong error message returned")

  def testPUTWithoutOriginFails(self):
    #This is run on prod with the prod dataset so mutating calls must fail and
    # tests must rely on checking for correct error
    # (IF test fails then it will return user creation not allowed because
    #  we will never allow user creation on the master tenant)
    PUTdict = { "invalid": True }
    loginDICT = containerTestCommon.getLoginDICTForDefaultUser(self)
    jwtToken = loginDICT['jwtData']['JWTToken']

    userName = "testSetUserName"
    registerJSON = {
      "authProviderGUID": "InvalidGUID",
      "credentialJSON": {
        "username": userName,
        "password": "InvalidPass"
       }
    }
    aa, res = callPutService(
      LOGIN, '/' + constants.masterTenantName + '/register',
      registerJSON,
      [401],
      loginDICT,
      headers=None,
      cookies=None,
      addOrigin=False
    )

    self.assertEqual(aa["message"], "Invalid Origin")


  def testGetWithoutOriginPasses(self):
    AuthProvidersDICT,res = callGetService(
      LOGIN, "/" + constants.masterTenantName + "/authproviders",
      [200],
      None,
      None,
      None,
      addOrigin=False
    )


'''
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
'''
