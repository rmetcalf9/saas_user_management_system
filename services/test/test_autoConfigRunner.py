#tests the autoconfig steps
import TestHelperSuperClass
import autoConfigRunner as autoConfig
from appObj import appObj
from unittest.mock import Mock, patch, call
from tenants import GetTenant, Login
from AuthProviders.authProviders_Internal import getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse

class helpers(TestHelperSuperClass.testHelperAPIClient):
  def assertNextLine(self, mocked_print, cur_line, expected):
    self.assertEqual(mocked_print.mock_calls[cur_line], call(expected))
    return cur_line + 1

  def assertHead(self, mocked_print):
    # returns number of lines
    l = 0
    l = self.assertNextLine(mocked_print, l, '\n----------------------------')
    l = self.assertNextLine(mocked_print, l, 'Running autoconfig...')
    l = self.assertNextLine(mocked_print, l, '----------------------------')
    return l

  def assertTail(self, mocked_print, l):
    l = self.assertNextLine(mocked_print, l, '----------------------------')
    l = self.assertNextLine(mocked_print, l, 'Autoconfig run complete')
    l = self.assertNextLine(mocked_print, l, '----------------------------\n\n')

    if len(mocked_print.mock_calls) == l:
      return
    self.assertEqual(l, len(mocked_print.mock_calls), msg="Not enough lines in output (next line=" + str(mocked_print.mock_calls[l]) + ")")

  def getCreateTenantStep(self, tenant="newTenant"):
    testStepData = {
      "tenantName": tenant,
      "description": "descrition of new tenant",
      "allowUserCreation": True,
      "JWTCollectionAllowedOriginList": [ "a", "b", "https://a.b.c.com" ]
    }
    return { "type": "createTenant", "data": testStepData}

  def getSetTenantJWTCollectionAllowedOriginListStep(self, tenant="newTenant", newVal=[ "a", "b", "https://a.b.c.com" ]):
    testStepData = {
      "tenantName": tenant,
      "JWTCollectionAllowedOriginList": newVal
    }
    return { "type": "setTenantJWTCollectionAllowedOriginList", "data": testStepData}

  #

  def getAddAuthStep(self, tenant="newTenant"):
    testStepData = {
      "tenantName": tenant,
      "menuText": "Test Menu Text",
      "iconLink": "Test Icon Link",
      "Type": "internal",
      "AllowUserCreation": True,
      "configJSON": {"userSufix": "@internalDataStore"},
      "AllowLink": True,
      "AllowUnlink": True,
      "LinkText": "Test Link Text"
    }
    return { "type": "addAuthProvider", "data": testStepData}

  def getAddInternalUserAccountStep(self, tenantName="newTenant", extraRoles=[]):
    testStepData = {
      "tenantName": tenantName,
      "userID": "123gfdds",
      "Username": "TestUser",
      "Password": "TestUser",
      "Roles": {
        tenantName: extraRoles
      } #has account always created
    }
    return { "type": "addInternalUserAccount", "data": testStepData}

#@TestHelperSuperClass.wipd
class test_appObjClass(helpers):
#Actual tests below

  def test_Echo(self):
    testType = "echo"
    testStepData = {"text": "Test Text To Echo"}
    autoConfigRunner = autoConfig.AutoConfigRunner(
      {"steps": [{ "type": testType, "data": testStepData}]}
    )
    with patch('builtins.print') as mocked_print:
      def runFn(storeConnection):
        autoConfigRunner.run(appObj, storeConnection)
      appObj.objectStore.executeInsideTransaction(runFn)
    l = self.assertHead(mocked_print)
    l = self.assertNextLine(mocked_print, l, 'Echo: Test Text To Echo')
    self.assertTail(mocked_print, l)

  def test_CreateTenant(self):
    testStep = self.getCreateTenantStep()
    autoConfigRunner = autoConfig.AutoConfigRunner(
      {"steps": [testStep]}
    )
    tenantObj = None
    with patch('builtins.print') as mocked_print:
      def runFn(storeConnection):
        autoConfigRunner.run(appObj, storeConnection)
      appObj.objectStore.executeInsideTransaction(runFn)
    l = self.assertHead(mocked_print)
    l = self.assertNextLine(mocked_print, l, 'CreateTenant: ' + testStep["data"]["tenantName"])
    self.assertTail(mocked_print, l)

    def runFn(storeConnection):
      return GetTenant(testStep["data"]["tenantName"], storeConnection, appObj=appObj)
    tenantObj = appObj.objectStore.executeInsideTransaction(runFn)

    self.assertNotEqual(tenantObj, None, msg="Tenant was not created")

    self.assertEqual(tenantObj.getName(), testStep["data"]["tenantName"])
    self.assertEqual(tenantObj._mainDict["Description"], testStep["data"]["description"])
    self.assertEqual(tenantObj.getAllowUserCreation(), testStep["data"]["allowUserCreation"])
    self.assertEqual(tenantObj.getJWTCollectionAllowedOriginList(), testStep["data"]["JWTCollectionAllowedOriginList"])

  def test_AddAuthProviderTenantNonExistantTenant(self):
    testStep = self.getAddAuthStep()
    autoConfigRunner = autoConfig.AutoConfigRunner(
      {"steps": [testStep]}
    )
    tenantObj = None
    def runFn(storeConnection):
      with self.assertRaises(Exception) as context:
        autoConfigRunner.run(appObj, storeConnection)
      self.assertEqual(str(context.exception), "AddAuthProvider: Tenant " + testStep["data"]["tenantName"] + " does not exist")
    appObj.objectStore.executeInsideTransaction(runFn)

  def test_AddTenantAndAuthProvider(self):
    testStep = self.getAddAuthStep()
    autoConfigRunner = autoConfig.AutoConfigRunner(
      {"steps": [
        self.getCreateTenantStep(),
        testStep
      ]}
    )
    tenantObj = None
    with patch('builtins.print') as mocked_print:
      def runFn(storeConnection):
        autoConfigRunner.run(appObj, storeConnection)
      appObj.objectStore.executeInsideTransaction(runFn)
    l = self.assertHead(mocked_print)
    l = self.assertNextLine(mocked_print, l, 'CreateTenant: ' + testStep["data"]["tenantName"])
    l = self.assertNextLine(mocked_print, l, 'AddAuthProvider: Type ' + testStep["data"]["Type"] + " added to Tenant " + testStep["data"]["tenantName"])
    self.assertTail(mocked_print, l)

    def runFn(storeConnection):
      return GetTenant(testStep["data"]["tenantName"], storeConnection, appObj=appObj)
    tenantObj = appObj.objectStore.executeInsideTransaction(runFn)

    self.assertEqual(tenantObj.getNumberOfAuthProviders(),1)

    authProvAdded = tenantObj.getAuthProvider(list(tenantObj.getAuthProviderGUIDList())[0])

    expected = {
      "AllowLink": True,
      "AllowUnlink": True,
      "AllowUserCreation": True,
      "ConfigJSON": {"userSufix": "@internalDataStore"},
      "IconLink": "Test Icon Link",
      "LinkText": "Test Link Text",
      "MenuText": "Test Menu Text",
      "Type": "internal"
    }
    self.assertJSONStringsEqualWithIgnoredKeys(authProvAdded, expected, ignoredKeys=["guid", "saltForPasswordHashing"])

  def test_AddInternalUserAccountTenantNonExistantTenant(self):
    testStep = self.getAddInternalUserAccountStep()
    autoConfigRunner = autoConfig.AutoConfigRunner(
      {"steps": [
        testStep
      ]}
    )
    tenantObj = None
    def runFn(storeConnection):
      with self.assertRaises(Exception) as context:
        autoConfigRunner.run(appObj, storeConnection)
      self.assertEqual(str(context.exception), "AddInternalUserAccount: Tenant " + testStep["data"]["tenantName"] + " does not exist")
    appObj.objectStore.executeInsideTransaction(runFn)

  def test_AddInternalUserAccountTenantNonExistantInternalAuth(self):
    testStep = self.getAddInternalUserAccountStep()
    autoConfigRunner = autoConfig.AutoConfigRunner(
      {"steps": [
        self.getCreateTenantStep(),
        testStep
      ]}
    )
    tenantObj = None
    def runFn(storeConnection):
      with self.assertRaises(Exception) as context:
        self.getCreateTenantStep(),
        autoConfigRunner.run(appObj, storeConnection)
      self.assertEqual(str(context.exception), "AddInternalUserAccount: Tenant " + testStep["data"]["tenantName"] + " does not have (exactly) one internal auth provider")
    appObj.objectStore.executeInsideTransaction(runFn)

  def test_AddInternalUserAccountTenantTwoInternalAuth(self):
    testStep = self.getAddInternalUserAccountStep()
    autoConfigRunner = autoConfig.AutoConfigRunner(
      {"steps": [
        self.getCreateTenantStep(),
        self.getAddAuthStep(),
        self.getAddAuthStep(),
        testStep
      ]}
    )
    tenantObj = None
    def runFn(storeConnection):
      with self.assertRaises(Exception) as context:
        self.getCreateTenantStep(),
        autoConfigRunner.run(appObj, storeConnection)
      self.assertEqual(str(context.exception), "AddInternalUserAccount: Tenant " + testStep["data"]["tenantName"] + " does not have (exactly) one internal auth provider")
    appObj.objectStore.executeInsideTransaction(runFn)

  def test_AddInternalUserAccountTenant(self):
    authTestStep = self.getAddAuthStep()
    testStep = self.getAddInternalUserAccountStep(tenantName="newTenant", extraRoles=["otherroletoadd"])
    autoConfigRunner = autoConfig.AutoConfigRunner(
      {"steps": [
        self.getCreateTenantStep(),
        authTestStep,
        testStep
      ]}
    )
    with patch('builtins.print') as mocked_print:
      def runFn(storeConnection):
        autoConfigRunner.run(appObj, storeConnection)
      appObj.objectStore.executeInsideTransaction(runFn)
    l = self.assertHead(mocked_print)
    l = self.assertNextLine(mocked_print, l, 'CreateTenant: ' + testStep["data"]["tenantName"])
    l = self.assertNextLine(mocked_print, l, 'AddAuthProvider: Type ' + authTestStep["data"]["Type"] + " added to Tenant " + authTestStep["data"]["tenantName"])
    l = self.assertNextLine(mocked_print, l, 'AddInternalUserAccount: Add ' + testStep["data"]["Username"] + " to tenant " + testStep["data"]["tenantName"])
    self.assertTail(mocked_print, l)

    def connectedFn(storeConnection):
      authProvider = GetTenant(authTestStep["data"]["tenantName"], storeConnection, appObj=appObj).getSingleAuthProviderOfType("internal")
      return Login(
        appObj=appObj,
        tenantName=testStep["data"]["tenantName"],
        authProviderGUID=authProvider["guid"],
        credentialJSON={
          "username": testStep["data"]["Username"],
          "password": getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(
            appObj, testStep["data"]["Username"], testStep["data"]["Password"], authProvider['saltForPasswordHashing'])
        },
        requestedUserID=testStep["data"]["userID"],
        storeConnection=storeConnection,
        a=None,b= None,c=None
      )
    loginResDict = appObj.objectStore.executeInsideTransaction(connectedFn)

    expected = {
      "ThisTenantRoles": ["hasaccount", "otherroletoadd"],
      "possibleUserIDs": None,
      "possibleUsers": None,
      "currentlyUsedAuthKey": "TestUser@internalDataStore_`@\\/'internal",
      "known_as": testStep["data"]["Username"],
      "other_data": {
        "createdBy": "autoConfigRunner/AddInternalUserAccount"
      },
      "userGuid": testStep["data"]["userID"]
    }

    self.assertJSONStringsEqualWithIgnoredKeys(loginResDict, expected, ignoredKeys=["authedPersonGuid", "currentlyUsedAuthProviderGuid", "jwtData", "refresh"])

  def test_SetTenantJWTCollectionAllowedOriginList_settovals_NonExistantTenant(self):
    testStep = self.getSetTenantJWTCollectionAllowedOriginListStep(tenant="someInvalidTenant")
    autoConfigRunner = autoConfig.AutoConfigRunner(
      {"steps": [
        testStep
      ]}
    )
    tenantObj = None
    def runFn(storeConnection):
      with self.assertRaises(Exception) as context:
        autoConfigRunner.run(appObj, storeConnection)
      self.assertEqual(str(context.exception), "SetTenantJWTCollectionAllowedOriginList: Tenant " + testStep["data"]["tenantName"] + " does not exist")
    appObj.objectStore.executeInsideTransaction(runFn)

  def test_SetTenantJWTCollectionAllowedOriginList_settovals(self):
    tenantToUse = "autocongifuteTestTenant"
    autoConfigRunner = autoConfig.AutoConfigRunner(
      {"steps": [
        self.getCreateTenantStep(tenant=tenantToUse),
        self.getAddAuthStep(tenant=tenantToUse)
      ]}
    )
    def setupFn(storeConnection):
      autoConfigRunner.run(appObj, storeConnection)
    appObj.objectStore.executeInsideTransaction(setupFn)

    for newValToSet in [ [""], [], ["a", "b"]]:
        print("Testing with newValToSet=", newValToSet)
        testStep = self.getSetTenantJWTCollectionAllowedOriginListStep(tenant=tenantToUse, newVal=newValToSet)
        autoConfigRunner = autoConfig.AutoConfigRunner(
          {"steps": [
            testStep
          ]}
        )
        with patch('builtins.print') as mocked_print:
          def runFn(storeConnection):
            autoConfigRunner.run(appObj, storeConnection)
          appObj.objectStore.executeInsideTransaction(runFn)
        l = self.assertHead(mocked_print)
        l = self.assertNextLine(mocked_print, l, 'SetTenantJWTCollectionAllowedOriginList: ' + testStep["data"]["tenantName"])
        self.assertTail(mocked_print, l)

        def runFn(storeConnection):
          return GetTenant(testStep["data"]["tenantName"], storeConnection, appObj=appObj)
        tenantObj = appObj.objectStore.executeInsideTransaction(runFn)

        self.assertNotEqual(tenantObj, None, msg="Tenant not found")

        self.assertEqual(tenantObj.getName(), testStep["data"]["tenantName"])
        self.assertEqual(tenantObj.getJWTCollectionAllowedOriginList(), newValToSet)
