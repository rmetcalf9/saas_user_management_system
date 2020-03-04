import TestHelperSuperClass
from ticketManager import ticketManagerClass
from appObj import appObj
import object_store_abstraction
import copy
import constants
import ticketManagerTestCommon

class helper(TestHelperSuperClass.testHelperAPIClient):
  def createTicketTypeFromDict(self, sampleTypeObj):
    def fn(storeConnection):
      tenantName = "NOTSET"
      if "tenantName" in sampleTypeObj:
        tenantName = sampleTypeObj["tenantName"]
      return appObj.TicketManager.upsertTicketType(tenantName=tenantName, ticketTypeDict=sampleTypeObj, objectVersion=None, storeConnection=storeConnection, appObj=appObj)
    return appObj.objectStore.executeInsideTransaction(fn)

@TestHelperSuperClass.wipd
class ticketManager(helper):
  def test_createTicketTypeWithEmptyDictThowsValidationException(self):
    with self.assertRaises(Exception) as context:
      self.createTicketTypeFromDict({})
    self.checkGotRightExceptionType(context, object_store_abstraction.RepositoryValidationException)

  def test_createTicketTypeWithValidDict(self):
    self.createTicketTypeFromDict(ticketManagerTestCommon.validTicketTypeDict)

  def test_createTicketTypeWithInvalidTenantName(self):
    invalidTickertTypeDict = copy.deepcopy(ticketManagerTestCommon.validTicketTypeDict)
    invalidTickertTypeDict["tenantName"] = "InvalidTenantName"
    with self.assertRaises(Exception) as context:
      self.createTicketTypeFromDict(invalidTickertTypeDict)
    self.checkGotRightException(context, constants.tenantDosentExistException)

