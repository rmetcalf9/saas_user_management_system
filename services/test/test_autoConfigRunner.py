#tests the autoconfig steps
import TestHelperSuperClass
import autoConfigRunner as autoConfig
from appObj import appObj
from unittest.mock import Mock, patch, call
from tenants import GetTenant

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

@TestHelperSuperClass.wipd
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
    testType = "createTenant"
    testStepData = {
      "tenantName": "newTenant",
      "description": "descrition of new tenant",
      "allowUserCreation": True,
      "JWTCollectionAllowedOriginList": [ "a", "b", "https://a.b.c.com" ]
    }
    autoConfigRunner = autoConfig.AutoConfigRunner(
      {"steps": [{ "type": testType, "data": testStepData}]}
    )
    tenantObj = None
    with patch('builtins.print') as mocked_print:
      def runFn(storeConnection):
        autoConfigRunner.run(appObj, storeConnection)
      appObj.objectStore.executeInsideTransaction(runFn)
    l = self.assertHead(mocked_print)
    l = self.assertNextLine(mocked_print, l, 'CreateTenant: ' + testStepData["tenantName"])
    self.assertTail(mocked_print, l)

    def runFn(storeConnection):
      return GetTenant(testStepData["tenantName"], storeConnection, appObj=appObj)
    tenantObj = appObj.objectStore.executeInsideTransaction(runFn)

    self.assertNotEqual(tenantObj, None, msg="Tenant was not created")

    self.assertEqual(tenantObj.getName(), testStepData["tenantName"])
    self.assertEqual(tenantObj._mainDict["Description"], testStepData["description"])
    self.assertEqual(tenantObj.getAllowUserCreation(), testStepData["allowUserCreation"])
    self.assertEqual(tenantObj.getJWTCollectionAllowedOriginList(), testStepData["JWTCollectionAllowedOriginList"])
