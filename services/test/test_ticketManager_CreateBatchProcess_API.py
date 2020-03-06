# This file throughly tests the create batch process
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
  def callBatchProcess(
      self,
      tenantName,
      ticketTypeID,
      foreignKeyList,
      foreignKeyDupAction,
      checkAndParseResponse = True
  ):
    postData = {
      "foreignKeyDupAction": foreignKeyDupAction,
      "foreignKeyList": foreignKeyList
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants/' + tenantName + '/tickettypes/' + ticketTypeID + '/createbatch',
      headers={constants.jwtHeaderName: self.getNormalJWTToken()},
      data=json.dumps(postData),
      content_type='application/json'
    )
    if not checkAndParseResponse:
      return result
    self.assertEqual(result.status_code, 200, msg="Err: " + result.get_data(as_text=True))
    return json.loads(result.get_data(as_text=True))

  def checkExpectedResults(self, resultJSON, keysExpected, issued, reissued, skipped, msg):
    self.assertEqual(resultJSON["stats"]["issued"],issued, msg="issued wrong - " + msg)
    self.assertEqual(resultJSON["stats"]["reissued"],reissued, msg="reissued wrong - " + msg)
    self.assertEqual(resultJSON["stats"]["skipped"],skipped, msg="skipped wrong - " + msg)
    self.assertEqual(len(resultJSON["results"]), len(keysExpected), msg="num keys wrong - " + msg)
    keysExpectedMap = {}
    for x in keysExpected:
      keysExpectedMap[x] = False
    for curResult in resultJSON["results"]:
      if curResult["foreignkey"] not in keysExpectedMap:
        self.assertTrue(False, msg="returned foreignkey not expected " + curResult["foreignkey"] + " - " + msg)
      if keysExpectedMap[curResult["foreignkey"]]:
        self.assertTrue(False, msg="foreignkey not in result more than once " + curResult["foreignkey"] + " - " + msg)
      keysExpectedMap[curResult["foreignkey"]] = True
      self.assertNotEqual(curResult["ticketGUID"], None, msg = "ticketGUID missing - " + msg )
      #Other result value is "ticketGUID" which is ignored because it could be anything

  def getTicketsForForeignKey(self, tenantName, ticketTypeID, foreignKey):
    params = {
      "query": foreignKey
    }
    result2 = self.testClient.get(
      self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants/' + tenantName + '/tickettypes/' + ticketTypeID + '/tickets?%s' % params,
      headers={constants.jwtHeaderName: self.getNormalJWTToken()},
      data=None,
      content_type='application/json'
    )
    self.assertEqual(result2.status_code, 200)
    ResultJSON = json.loads(result2.get_data(as_text=True))

    return ResultJSON["result"]

@TestHelperSuperClass.wipd
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
      foreignKeyDupAction="ReissueNonActive",
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
      foreignKeyDupAction= "ReissueNonActive",
      checkAndParseResponse = True
    )
    self.checkExpectedResults(resultJSON=resultJSON, keysExpected=[ "fk@testfj.com" ], issued=1, reissued=0, skipped=0, msg="None")

    ticketsJSON = self.getTicketsForForeignKey(
      tenantName=setupData["ticketTypeNewTanent"]["tenantName"],
      ticketTypeID=setupData["ticketTypeNewTanent"]["id"],
      foreignKey="fk@testfj.com"
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
      }
    }
    python_Testing_Utilities.assertObjectsEqual(
      unittestTestCaseClass=self,
      first=ticketsJSON[0],
      second=expectedTicketJSON,
      msg="JSON of created Ticket is not what was expected",
      ignoredRootKeys=[]
    )


#Def run single process twice no conflicts

#Def run single process twice one conflicts - skip

#Def run single process twice one conflicts - reissue



#TODO And transfer to another file
# dest