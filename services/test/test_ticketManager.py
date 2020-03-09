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

  def deleteTicketType(self, tenantName, ticketTypeDict):
    def fn(storeConnection):
      return appObj.TicketManager.deleteTicketType(
        tenantName=tenantName,
        tickettypeID=ticketTypeDict["id"],
        ObjectVersionNumber=ticketTypeDict[object_store_abstraction.RepositoryObjBaseClass.getMetadataElementKey()]["objectVersion"],
        storeConnection=storeConnection
      )
    return appObj.objectStore.executeInsideTransaction(fn)

  def getTicketTypeTicketObject(self, ticketTypeID):
    def fn(storeConnection):
      return appObj.TicketManager.repositoryTicketTypeTickets.get(id=ticketTypeID, storeConnection=storeConnection)
    return appObj.objectStore.executeInsideTransaction(fn)

  def createSomeTickets(self, tenantName, tickettypeID, foreignKeyDupAction="Skip"):
    def fn(storeConnection):
      return appObj.TicketManager.createBatchProcess(
        tenantName=tenantName,
        tickettypeID=tickettypeID,
        foreignKeyDupAction=foreignKeyDupAction,
        foreignKeyList=["1@1","2@1","3@1","4@1","5@1","6@1"],
        storeConnection=storeConnection,
        appObj=appObj
      )
    return appObj.objectStore.executeInsideTransaction(fn)

  def getTicket(self, ticketID):
    def fn(storeConnection):
      return appObj.TicketManager.repositoryTicket.get(id=ticketID, storeConnection=storeConnection)
    return appObj.objectStore.executeInsideTransaction(fn)

  def getTicketType(self, tenantName, tickettypeID):
    def fn(storeConnection):
      return appObj.TicketManager.getTicketType(
        tenantName=tenantName,
        tickettypeID=tickettypeID,
        storeConnection=storeConnection
      )
    return appObj.objectStore.executeInsideTransaction(fn)


#@TestHelperSuperClass.wipd
class ticketManagerTests(helper):
  def test_createTicketTypeWithEmptyDictThowsValidationException(self):
    with self.assertRaises(Exception) as context:
      self.createTicketTypeFromDict({})
    self.checkGotRightExceptionType(context, object_store_abstraction.RepositoryValidationException)

  def test_createTicketTypeWithValidDict(self):
    self.createTicketTypeFromDict(ticketManagerTestCommon.validTicketTypeDict)

  def test_createTicketTypeWithInvalidTenantName(self):
    invalidTicketTypeDict = copy.deepcopy(ticketManagerTestCommon.validTicketTypeDict)
    invalidTicketTypeDict["tenantName"] = "InvalidTenantName"
    with self.assertRaises(Exception) as context:
      self.createTicketTypeFromDict(invalidTicketTypeDict)
    self.checkGotRightException(context, constants.tenantDosentExistException)

  def test_deleteTicketTypeCleansUpTicketTypeTicketObject(self):
    ticketTypeObj = self.createTicketTypeFromDict(ticketManagerTestCommon.validTicketTypeDict)
    ticketTypeID = ticketTypeObj.getDict()["id"]
    self.createSomeTickets(tenantName=ticketManagerTestCommon.validTicketTypeDict["tenantName"], tickettypeID=ticketTypeID)
    self.assertNotEqual(self.getTicketTypeTicketObject(ticketTypeID=ticketTypeID),None, msg="No tickettypeticket object created")

    deleteResponse = self.deleteTicketType(tenantName=ticketManagerTestCommon.validTicketTypeDict["tenantName"], ticketTypeDict=ticketTypeObj.getDict())
    self.assertEqual(deleteResponse[0]["response"],"OK", msg="Delete failed")
    ticketTypeTicketObj = self.getTicketTypeTicketObject(ticketTypeID=ticketTypeID)
    self.assertEqual(ticketTypeTicketObj, None, msg="TicketTypeTicket object was not cleanned up")

  def test_deleteTicketTypeCleansUpTickets(self):
    ticketTypeObj = self.createTicketTypeFromDict(ticketManagerTestCommon.validTicketTypeDict)
    ticketTypeID = ticketTypeObj.getDict()["id"]
    createTicketReturn = self.createSomeTickets(tenantName=ticketManagerTestCommon.validTicketTypeDict["tenantName"], tickettypeID=ticketTypeID)

    deleteResponse = self.deleteTicketType(tenantName=ticketManagerTestCommon.validTicketTypeDict["tenantName"], ticketTypeDict=ticketTypeObj.getDict())
    self.assertEqual(deleteResponse[0]["response"],"OK", msg="Delete failed")

    for curResult in createTicketReturn[0]["results"]:
      ticketObj = self.getTicket(ticketID=curResult["ticketGUID"])
      self.assertEqual(ticketObj, None, msg="Failed to delete ticket")

  def test_deleteTicketTypeCleansReissuedUpTickets(self):
    ticketTypeObj = self.createTicketTypeFromDict(ticketManagerTestCommon.validTicketTypeDict)
    ticketTypeID = ticketTypeObj.getDict()["id"]
    createTicketReturn = self.createSomeTickets(tenantName=ticketManagerTestCommon.validTicketTypeDict["tenantName"], tickettypeID=ticketTypeID)
    self.assertEqual(createTicketReturn[0]["stats"]["issued"], 6)
    self.assertEqual(createTicketReturn[1], 200)
    reissueTicketReturn = self.createSomeTickets(tenantName=ticketManagerTestCommon.validTicketTypeDict["tenantName"], tickettypeID=ticketTypeID, foreignKeyDupAction="ReissueAll")
    self.assertEqual(reissueTicketReturn[1], 200)
    self.assertEqual(reissueTicketReturn[0]["stats"]["reissued"], 6)

    # need to get a new object because object version will update
    ticketTypeGetResponse = self.getTicketType(tenantName=ticketManagerTestCommon.validTicketTypeDict["tenantName"], tickettypeID=ticketTypeID)

    deleteResponse = self.deleteTicketType(
      tenantName=ticketManagerTestCommon.validTicketTypeDict["tenantName"],
      ticketTypeDict=ticketTypeGetResponse.getDict()
    )
    self.assertEqual(deleteResponse[0]["response"],"OK", msg="Delete failed")

    for curResult in createTicketReturn[0]["results"]:
      ticketObj = self.getTicket(ticketID=curResult["ticketGUID"])
      self.assertEqual(ticketObj, None, msg="Failed to delete orig ticket - " + curResult["ticketGUID"])

    for curResult in reissueTicketReturn[0]["results"]:
      ticketObj = self.getTicket(ticketID=curResult["ticketGUID"])
      self.assertEqual(ticketObj, None, msg="Failed to delete reissued ticket")
