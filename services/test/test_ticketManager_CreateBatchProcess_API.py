# This file throughly tests the create batch process
import TestHelperSuperClass
from appObj import appObj
import object_store_abstraction
import copy
import constants
import ticketManagerTestCommon
from ticketManager__Common_API import ticketManagerAPICommonUtilsClass
import json

class helper(ticketManagerAPICommonUtilsClass):
  def setupNewTenantAndTicketType(self, tenantData, ticketTypeName):
    tenantJSON = self.createTenantForTesting(tenantData)
    ticketType = self.createTicketType(constants.masterTenantName, overrideName=ticketTypeName)
    return {
      "tenantJSON": tenantJSON,
      "ticketType": ticketType
    }
  def callBatchProcess(
      self,
      tenantName,
      ticketTypeID,
      forigenKeyList,
      forigenKeyDupAction,
      checkAndParseResponse = True
  ):
    postData = {
      "forigenKeyDupAction": forigenKeyDupAction,
      "forigenKeyList": forigenKeyList
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
    self.assertEqual(resultJSON["stats"]["issued"],issues, "issued wrong - " + msg)
    self.assertEqual(resultJSON["stats"]["reissued"],reissued, "reissued wrong - " + msg)
    self.assertEqual(resultJSON["stats"]["skipped"],skipped, "skipped wrong - " + msg)
    self.assertEqual(resultJSON["results"], len(keysExpected), "num keys wrong - " + msg)
    keysExpectedMap = {}
    for x in keysExpected:
      keysExpectedMap[x] = False
    for curResult in resultJSON["results"]:
      if curResult["key"] not in keysExpectedMap:
        self.assertTrue(False, "key not in result " + curResult["key"] + " - " + msg)
      if curResult["key"]:
        self.assertTrue(False, "key not in result more than once " + curResult["key"] + " - " + msg)
      curResult["key"] = True

@TestHelperSuperClass.wipd
class ticketManager_CreateBatchProcess(helper):
  def test_InvalidForeignKeyAction(self):
    testTicketTypeName = "TestType001"
    setupData = self.setupNewTenantAndTicketType(tenantData=TestHelperSuperClass.tenantWithNoAuthProviders,
                                                 ticketTypeName=testTicketTypeName)
    resultRAW = self.callBatchProcess(
      tenantName=setupData["tenantJSON"]["Name"],
      ticketTypeID=setupData["ticketType"]["id"],
      forigenKeyList=["fk@testfj.com"],
      forigenKeyDupAction="ReissueNonActive",
      checkAndParseResponse=False
    )
    self.assertEqual(resultRAW.status_code, 400, msg="Err: " + resultRAW.get_data(as_text=True))

  def test_createSingleValidTicket(self):
    testTicketTypeName = "TestType001"
    setupData = self.setupNewTenantAndTicketType(tenantData=TestHelperSuperClass.tenantWithNoAuthProviders, ticketTypeName=testTicketTypeName)
    resultJSON = self.callBatchProcess(
      tenantName=setupData["tenantJSON"]["Name"],
      ticketTypeID=setupData["ticketType"]["id"],
      forigenKeyList= [ "fk@testfj.com" ],
      forigenKeyDupAction= "ReissueNonActive",
      checkAndParseResponse = True
    )
    self.checkExpectedResults(resultJSON=resultJSON, keysExpected=[ "fk@testfj.com" ], issued=1, reissued=0, skipped=0, msg="None")
