import TestHelperSuperClass
from ticketManager__Common_API import ticketManagerAPICommonUtilsClass
import datetime
import pytz
from appObj import appObj
import json
import copy
import python_Testing_Utilities

class helper(ticketManagerAPICommonUtilsClass):
  def setEnabledForTicketType(self, ticketType, newValue):
    newDict = copy.deepcopy(ticketType)
    newDict["enabled"] = newValue
    response = self.updateTicketType(ticketTypeID=newDict["id"], ticketTypeTenant=newDict["tenantName"], newDict=newDict, checkAndParseResponse=True)
    return response

#@TestHelperSuperClass.wipd
class ticketManager_ViewTickets_API(helper):
  def test_GetTicket(self):
    testTime1 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime1)
    setup = self.setupTenantsTicketTypesAndTickets()
    tenantUsedInTest = setup["tenants"][0]
    tenantName = tenantUsedInTest["tenantJSON"]["Name"]
    ticketTypeUsedInTest=tenantUsedInTest["ticketTypes"][1]
    ticketTypeID=tenantUsedInTest["ticketTypes"][1]["createTicketTypeResult"]["id"]
    ticketTypeName=tenantUsedInTest["ticketTypes"][1]["createTicketTypeResult"]["ticketTypeName"]
    ticketUsedInTest=tenantUsedInTest["ticketTypes"][1]["ticketCreationProcessResult"]["results"][1]
    ticketGUID=tenantUsedInTest["ticketTypes"][1]["ticketCreationProcessResult"]["results"][1]["ticketGUID"]
    ticketForeignKey=tenantUsedInTest["ticketTypes"][1]["ticketCreationProcessResult"]["results"][1]["foreignKey"]

    result = self.testClient.get(
      self.loginAPIPrefix + '/' + tenantName + '/tickets/' + ticketGUID,
      headers={"Origin": TestHelperSuperClass.httpOrigin}
    )
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

    expectedResult = {
      "ticketType": copy.deepcopy(ticketTypeUsedInTest["createTicketTypeResult"]),
      "isUsable": "USABLE",
      "expiry": (testTime1 + datetime.timedelta(hours=int(ticketTypeUsedInTest["createTicketTypeResult"]["issueDuration"]))).isoformat()
    }
    python_Testing_Utilities.assertObjectsEqual(
      unittestTestCaseClass=self,
      first=resultJSON,
      second=expectedResult,
      msg="Didn't get expected result",
      ignoredRootKeys=[]
    )

  def test_GetTicketOfDisabledTicketType(self):
    testTime1 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime1)
    setup = self.setupTenantsTicketTypesAndTickets()
    tenantUsedInTest = setup["tenants"][0]
    tenantName = tenantUsedInTest["tenantJSON"]["Name"]
    ticketTypeUsedInTest=tenantUsedInTest["ticketTypes"][1]
    ticketTypeID=tenantUsedInTest["ticketTypes"][1]["createTicketTypeResult"]["id"]
    ticketTypeName=tenantUsedInTest["ticketTypes"][1]["createTicketTypeResult"]["ticketTypeName"]
    ticketUsedInTest=tenantUsedInTest["ticketTypes"][1]["ticketCreationProcessResult"]["results"][1]
    ticketGUID=tenantUsedInTest["ticketTypes"][1]["ticketCreationProcessResult"]["results"][1]["ticketGUID"]
    ticketForeignKey=tenantUsedInTest["ticketTypes"][1]["ticketCreationProcessResult"]["results"][1]["foreignKey"]

    ticketTypeUsedInTest["createTicketTypeResult"] = self.setEnabledForTicketType(ticketType=ticketTypeUsedInTest["createTicketTypeResult"], newValue=False)

    result = self.testClient.get(
      self.loginAPIPrefix + '/' + tenantName + '/tickets/' + ticketGUID,
      headers={"Origin": TestHelperSuperClass.httpOrigin}
    )
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

    expectedResult = {
      "ticketType": copy.deepcopy(ticketTypeUsedInTest["createTicketTypeResult"]),
      "isUsable": "INVALID",
      "expiry": (testTime1 + datetime.timedelta(hours=int(ticketTypeUsedInTest["createTicketTypeResult"]["issueDuration"]))).isoformat()
    }
    python_Testing_Utilities.assertObjectsEqual(
      unittestTestCaseClass=self,
      first=resultJSON,
      second=expectedResult,
      msg="Didn't get expected result",
      ignoredRootKeys=[]
    )


  def test_GetTicketThatHasExpired(self):
    testTime1 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime1)
    setup = self.setupTenantsTicketTypesAndTickets()
    tenantUsedInTest = setup["tenants"][0]
    tenantName = tenantUsedInTest["tenantJSON"]["Name"]
    ticketTypeUsedInTest = tenantUsedInTest["ticketTypes"][1]
    ticketTypeID = tenantUsedInTest["ticketTypes"][1]["createTicketTypeResult"]["id"]
    ticketTypeName = tenantUsedInTest["ticketTypes"][1]["createTicketTypeResult"]["ticketTypeName"]
    ticketUsedInTest = tenantUsedInTest["ticketTypes"][1]["ticketCreationProcessResult"]["results"][1]
    ticketGUID = tenantUsedInTest["ticketTypes"][1]["ticketCreationProcessResult"]["results"][1]["ticketGUID"]
    ticketForeignKey = tenantUsedInTest["ticketTypes"][1]["ticketCreationProcessResult"]["results"][1]["foreignKey"]

    testTime2 = (testTime1 + datetime.timedelta(hours=int(1 + ticketTypeUsedInTest["createTicketTypeResult"]["issueDuration"])))
    appObj.setTestingDateTime(testTime2)

    result = self.testClient.get(
      self.loginAPIPrefix + '/' + tenantName + '/tickets/' + ticketGUID,
      headers={"Origin": TestHelperSuperClass.httpOrigin}
    )
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

    expectedResult = {
      "ticketType": copy.deepcopy(ticketTypeUsedInTest["createTicketTypeResult"]),
      "isUsable": "EXPIRED",
      "expiry": (testTime1 + datetime.timedelta(
        hours=int(ticketTypeUsedInTest["createTicketTypeResult"]["issueDuration"]))).isoformat()
    }
    python_Testing_Utilities.assertObjectsEqual(
      unittestTestCaseClass=self,
      first=resultJSON,
      second=expectedResult,
      msg="Didn't get expected result",
      ignoredRootKeys=[]
    )