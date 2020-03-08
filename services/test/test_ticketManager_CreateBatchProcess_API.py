# This file thoroughly tests the create batch process
import TestHelperSuperClass
from appObj import appObj
import object_store_abstraction
import copy
import constants
import ticketManagerTestCommon
from ticketManager__Common_API import ticketManagerAPICommonUtilsClass
import json
import datetime
import pytz
import python_Testing_Utilities

class helper(ticketManagerAPICommonUtilsClass):
  def setupNewTenantAndTicketType(self, tenantData, ticketTypeName):
    tenantJSON = self.createTenantForTesting(tenantData)
    ticketTypeMaster = self.createTicketType(constants.masterTenantName, overrideName=ticketTypeName)
    ticketTypeNewTanent = self.createTicketType(tenantData["Name"], overrideName=ticketTypeName)
    return {
      "tenantJSON": tenantJSON,
      "ticketTypeMaster": ticketTypeMaster,
      "ticketTypeNewTanent": ticketTypeNewTanent
    }

  def checkExpectedResults(self, resultJSON, keysExpected, issued, reissued, skipped, msg):
    self.assertEqual(resultJSON["stats"]["issued"],issued, msg="issued wrong - " + msg)
    self.assertEqual(resultJSON["stats"]["reissued"],reissued, msg="reissued wrong - " + msg)
    self.assertEqual(resultJSON["stats"]["skipped"],skipped, msg="skipped wrong - " + msg)
    self.assertEqual(len(resultJSON["results"]), len(keysExpected), msg="num keys wrong (got " + str(len(resultJSON["results"])) + " expected " + str(len(keysExpected)) + ") - " + msg)
    keysExpectedMap = {}
    for x in keysExpected:
      keysExpectedMap[x] = False
    for curResult in resultJSON["results"]:
      if curResult["foreignKey"] not in keysExpectedMap:
        self.assertTrue(False, msg="returned foreignKey not expected " + curResult["foreignKey"] + " - " + msg)
      if keysExpectedMap[curResult["foreignKey"]]:
        self.assertTrue(False, msg="foreignKey not in result more than once " + curResult["foreignKey"] + " - " + msg)
      keysExpectedMap[curResult["foreignKey"]] = True
      self.assertNotEqual(curResult["ticketGUID"], None, msg = "ticketGUID missing - " + msg )
      #Other result value is "ticketGUID" which is ignored because it could be anything

#@TestHelperSuperClass.wipd
class ticketManager_CreateBatchProcess(helper):
  def test_InvalidForeignKeyAction(self):
    testTicketTypeName = "TestType001"
    setupData = self.setupNewTenantAndTicketType(tenantData=TestHelperSuperClass.tenantWithNoAuthProviders,
                                                 ticketTypeName=testTicketTypeName)
    resultRAW = self.callBatchProcess(
      tenantName=setupData["ticketTypeNewTanent"]["tenantName"],
      ticketTypeID=setupData["ticketTypeNewTanent"]["id"],
      foreignKeyList=["fk@testfj.com"],
      foreignKeyDupAction="InvalidAction",
      checkAndParseResponse=False
    )
    self.assertEqual(resultRAW.status_code, 400, msg="Err: " + resultRAW.get_data(as_text=True))

  def def_test_ticketTypeNotFound(self):
    testTicketTypeName = "TestType001"
    setupData = self.setupNewTenantAndTicketType(tenantData=TestHelperSuperClass.tenantWithNoAuthProviders,
                                                 ticketTypeName=testTicketTypeName)
    resultRAW = self.callBatchProcess(
      tenantName=setupData["tenantJSON"]["Name"],
      ticketTypeID="SomeUnknownTicketTypeID",
      foreignKeyList=["fk@testfj.com"],
      foreignKeyDupAction="ReissueAll",
      checkAndParseResponse=False
    )
    self.assertEqual(resultRAW.status_code, 404, msg="Err: " + resultRAW.get_data(as_text=True))

  def test_createSingleValidTicket(self):
    testTime1 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime1)
    testTicketTypeName = "TestType001"
    setupData = self.setupNewTenantAndTicketType(tenantData=TestHelperSuperClass.tenantWithNoAuthProviders, ticketTypeName=testTicketTypeName)

    testTime2 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime2)
    resultJSON = self.callBatchProcess(
      tenantName=setupData["ticketTypeNewTanent"]["tenantName"],
      ticketTypeID=setupData["ticketTypeNewTanent"]["id"],
      foreignKeyList= [ "fk@testfj.com" ],
      foreignKeyDupAction= "ReissueAllActive",
      checkAndParseResponse = True
    )
    self.checkExpectedResults(resultJSON=resultJSON, keysExpected=[ "fk@testfj.com" ], issued=1, reissued=0, skipped=0, msg="None")

    ticketsJSON = self.queryForTickets(
      tenantName=setupData["ticketTypeNewTanent"]["tenantName"],
      ticketTypeID=setupData["ticketTypeNewTanent"]["id"],
      queryString="fk@testfj.com"
    )
    self.assertEqual(len(ticketsJSON), 1, msg="Should have found a single ticket")
    expectedTicketJSON = {
      "id": resultJSON["results"][0]["ticketGUID"],
      "typeGUID": setupData["ticketTypeNewTanent"]["id"],
      "expiry": (testTime2 + datetime.timedelta(hours=int(setupData["ticketTypeNewTanent"]["issueDuration"]))).isoformat(),
      "foreignKey": "fk@testfj.com",
      "usedDate": None,
      "useWithUserID": None,
      "reissueRequestedDate": None,
      "reissuedTicketID": None,
      "disabled": False,
      object_store_abstraction.RepositoryObjBaseClass.getMetadataElementKey(): {
        "creationDateTime": testTime2.isoformat(),
        "lastUpdateDateTime": testTime2.isoformat(),
        "objectKey": resultJSON["results"][0]["ticketGUID"],
        "objectVersion": "1"
      },
      "usableState": "US_USABLEIFTICKETTYPEISENABLED"
    }
    python_Testing_Utilities.assertObjectsEqual(
      unittestTestCaseClass=self,
      first=ticketsJSON[0],
      second=expectedTicketJSON,
      msg="JSON of created Ticket is not what was expected",
      ignoredRootKeys=[]
    )

  def test_createSingleValidTicketTwiceAndCheckWeHaveTwoTickets(self):
    testTime1 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime1)
    testTicketTypeName = "TestType001"
    setupData = self.setupNewTenantAndTicketType(tenantData=TestHelperSuperClass.tenantWithNoAuthProviders, ticketTypeName=testTicketTypeName)

    foreignKeyList001 = ["fk@testfj.com"]
    foreignKeyList002 = ["second@testfj.com"]

    testTime2 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime2)
    resultJSON = self.callBatchProcess(
      tenantName=setupData["ticketTypeNewTanent"]["tenantName"],
      ticketTypeID=setupData["ticketTypeNewTanent"]["id"],
      foreignKeyList= foreignKeyList001,
      foreignKeyDupAction= "ReissueAllActive",
      checkAndParseResponse = True
    )
    self.checkExpectedResults(resultJSON=resultJSON, keysExpected=foreignKeyList001, issued=1, reissued=0, skipped=0, msg="None")

    testTime3 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime2)
    resultJSON = self.callBatchProcess(
      tenantName=setupData["ticketTypeNewTanent"]["tenantName"],
      ticketTypeID=setupData["ticketTypeNewTanent"]["id"],
      foreignKeyList= foreignKeyList002,
      foreignKeyDupAction= "ReissueAllActive",
      checkAndParseResponse = True
    )
    self.checkExpectedResults(resultJSON=resultJSON, keysExpected=foreignKeyList002, issued=1, reissued=0, skipped=0, msg="None")

    ticketsJSON = self.queryForTickets(
      tenantName=setupData["ticketTypeNewTanent"]["tenantName"],
      ticketTypeID=setupData["ticketTypeNewTanent"]["id"],
      queryString=None
    )
    self.assertEqual(len(ticketsJSON), 2, msg="Should have found two tickets")
    allKeys = []
    for curTicket in ticketsJSON:
      allKeys.append(curTicket["foreignKey"])

    python_Testing_Utilities.assertObjectsEqual(
      unittestTestCaseClass=self,
      first=allKeys,
      second=foreignKeyList001 + foreignKeyList002,
      msg="JSON of created Ticket is not what was expected",
      ignoredRootKeys=[]
    )

  def test_createSameSingleValidTicketTwiceAndCheckWeHaveOneTicket_inSkipMode(self):
    testTime1 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime1)
    testTicketTypeName = "TestType001"
    setupData = self.setupNewTenantAndTicketType(tenantData=TestHelperSuperClass.tenantWithNoAuthProviders, ticketTypeName=testTicketTypeName)

    foreignKeyList001 = ["fk@testfj.com"]

    testTime2 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime2)
    resultJSON = self.callBatchProcess(
      tenantName=setupData["ticketTypeNewTanent"]["tenantName"],
      ticketTypeID=setupData["ticketTypeNewTanent"]["id"],
      foreignKeyList= foreignKeyList001,
      foreignKeyDupAction= "ReissueAllActive",
      checkAndParseResponse = True
    )
    self.checkExpectedResults(resultJSON=resultJSON, keysExpected=foreignKeyList001, issued=1, reissued=0, skipped=0, msg="None")

    testTime3 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime2)
    resultJSON = self.callBatchProcess(
      tenantName=setupData["ticketTypeNewTanent"]["tenantName"],
      ticketTypeID=setupData["ticketTypeNewTanent"]["id"],
      foreignKeyList= foreignKeyList001,
      foreignKeyDupAction= "Skip",
      checkAndParseResponse = True
    )
    self.checkExpectedResults(resultJSON=resultJSON, keysExpected=[], issued=0, reissued=0, skipped=1, msg="None")

    ticketsJSON = self.queryForTickets(
      tenantName=setupData["ticketTypeNewTanent"]["tenantName"],
      ticketTypeID=setupData["ticketTypeNewTanent"]["id"],
      queryString=None # results in all being returned
    )
    self.assertEqual(len(ticketsJSON), 1, msg="Should have found one ticket")
    allKeys = []
    for curTicket in ticketsJSON:
      allKeys.append(curTicket["foreignKey"])

    python_Testing_Utilities.assertObjectsEqual(
      unittestTestCaseClass=self,
      first=allKeys,
      second=foreignKeyList001,
      msg="JSON of created Ticket is not what was expected",
      ignoredRootKeys=[]
    )

  def test_createSameSingleValidTicketTwiceAndCheckWeHaveOneTicket_inReissueMode(self):
    testTime1 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime1)
    testTicketTypeName = "TestType001"
    setupData = self.setupNewTenantAndTicketType(tenantData=TestHelperSuperClass.tenantWithNoAuthProviders, ticketTypeName=testTicketTypeName)

    foreignKeyList001 = ["fk@testfj.com"]

    testTime2 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime2)
    resultJSON = self.callBatchProcess(
      tenantName=setupData["ticketTypeNewTanent"]["tenantName"],
      ticketTypeID=setupData["ticketTypeNewTanent"]["id"],
      foreignKeyList= foreignKeyList001,
      foreignKeyDupAction= "ReissueAllActive",
      checkAndParseResponse = True
    )
    self.checkExpectedResults(resultJSON=resultJSON, keysExpected=foreignKeyList001, issued=1, reissued=0, skipped=0, msg="None")
    origTicketID = resultJSON["results"][0]["ticketGUID"]

    testTime3 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime2)
    resultJSON = self.callBatchProcess(
      tenantName=setupData["ticketTypeNewTanent"]["tenantName"],
      ticketTypeID=setupData["ticketTypeNewTanent"]["id"],
      foreignKeyList= foreignKeyList001,
      foreignKeyDupAction= "ReissueAllActive",
      checkAndParseResponse = True
    )
    self.checkExpectedResults(resultJSON=resultJSON, keysExpected=foreignKeyList001, issued=0, reissued=1, skipped=0, msg="None")
    reissuedTicketID = resultJSON["results"][0]["ticketGUID"]

    ticketsJSON = self.queryForTickets(
      tenantName=setupData["ticketTypeNewTanent"]["tenantName"],
      ticketTypeID=setupData["ticketTypeNewTanent"]["id"],
      queryString=None # results in all being returned
    )
    self.assertEqual(len(ticketsJSON), 2, msg="Should have found two tickets because previous and new")
    allKeys = []
    for curTicket in ticketsJSON:
      allKeys.append(curTicket["foreignKey"])

    python_Testing_Utilities.assertObjectsEqual(
      unittestTestCaseClass=self,
      first=allKeys,
      second=foreignKeyList001 + foreignKeyList001,
      msg="JSON of created Ticket is not what was expected",
      ignoredRootKeys=[]
    )

    #Make sure old ticket has new tickets reissueID
    origTicket = None
    for curTicket in ticketsJSON:
      if curTicket["id"] == origTicketID:
        if origTicket is not None:
          self.assertTrue(False, msg="There should not be mutiple orig tickets in query result")
        origTicket = curTicket

    self.assertEqual(origTicket["reissuedTicketID"], reissuedTicketID, msg="Reissued ID not set on original ticket")



#TODO And transfer to another file
# dest