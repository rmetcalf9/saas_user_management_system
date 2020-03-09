import TestHelperSuperClass
from ticketManager__Common_API import ticketManagerAPICommonUtilsClass
import copy
import python_Testing_Utilities
import datetime
import pytz
from appObj import appObj
import object_store_abstraction

class helper(ticketManagerAPICommonUtilsClass):
  pass

#@TestHelperSuperClass.wipd
class ticketManager_ViewTickets_API(helper):
  def test_QueryBackAllTicketsOfType(self):
    setup = self.setupTenantsTicketTypesAndTickets()

    resultJSON = self.queryForTickets(tenantName=setup["tenants"][0]["tenantJSON"]["Name"], ticketTypeID=setup["tenants"][0]["ticketTypes"][1]["createTicketTypeResult"]["id"], queryString=None)
    self.assertEqual(len(resultJSON),6,msg="Wrong number of tickets returned")

    issuedTicketIDS = []
    for curCreationRes in setup["tenants"][0]["ticketTypes"][1]["ticketCreationProcessResult"]["results"]:
      issuedTicketIDS.append(curCreationRes["ticketGUID"])

    queriedTicketIDS = []
    for curResult in resultJSON:
      queriedTicketIDS.append(curResult["id"])

    python_Testing_Utilities.assertObjectsEqual(
      unittestTestCaseClass=self,
      first=issuedTicketIDS,
      second=queriedTicketIDS,
      msg="Different tickets queried back",
      ignoredRootKeys=[]
    )

  def test_QueryBackSingleTicket(self):
    setup = self.setupTenantsTicketTypesAndTickets()

    ticketToQueryBack = setup["tenants"][0]["ticketTypes"][1]["ticketCreationProcessResult"]["results"][4]

    resultJSON = self.queryForTickets(
      tenantName=setup["tenants"][0]["tenantJSON"]["Name"],
      ticketTypeID=setup["tenants"][0]["ticketTypes"][1]["createTicketTypeResult"]["id"],
      queryString=ticketToQueryBack["foreignKey"]
    )
    self.assertEqual(len(resultJSON),1,msg="Wrong number of tickets returned")

    self.assertEqual(resultJSON[0]["id"], ticketToQueryBack["ticketGUID"])
    self.assertEqual(resultJSON[0]["foreignKey"], ticketToQueryBack["foreignKey"])
    self.assertEqual(resultJSON[0]["usableState"], "US_USABLEIFTICKETTYPEISENABLED")

  def test_QueryBackTicketAfterExpiry(self):
    testTime1 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime1)
    setup = self.setupTenantsTicketTypesAndTickets()

    ticketToQueryBack = setup["tenants"][0]["ticketTypes"][1]["ticketCreationProcessResult"]["results"][4]

    testTime2 = datetime.datetime.now(pytz.timezone("UTC")) + datetime.timedelta(hours=int(1 + setup["tenants"][0]["ticketTypes"][1]["createTicketTypeResult"]["issueDuration"]))
    appObj.setTestingDateTime(testTime2)

    resultJSON = self.queryForTickets(
      tenantName=setup["tenants"][0]["tenantJSON"]["Name"],
      ticketTypeID=setup["tenants"][0]["ticketTypes"][1]["createTicketTypeResult"]["id"],
      queryString=ticketToQueryBack["foreignKey"]
    )
    self.assertEqual(len(resultJSON),1,msg="Wrong number of tickets returned")

    self.assertEqual(resultJSON[0]["id"], ticketToQueryBack["ticketGUID"])
    self.assertEqual(resultJSON[0]["foreignKey"], ticketToQueryBack["foreignKey"])
    self.assertEqual(resultJSON[0]["usableState"], "US_EXPIRED")

  def test_queryBackOnlyExpiredTickets(self):
    testTime1 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime1)
    setup = self.setupTenantsTicketTypesAndTickets()

    ticketTypeToQueryBack = setup["tenants"][0]["ticketTypes"][1]
    ticketToQueryBack = ticketTypeToQueryBack["ticketCreationProcessResult"]["results"][4]

    testTime2 = datetime.datetime.now(pytz.timezone("UTC")) + datetime.timedelta(hours=int(1 + setup["tenants"][0]["ticketTypes"][1]["createTicketTypeResult"]["issueDuration"]))
    appObj.setTestingDateTime(testTime2)

    # Add a ticket that is not expired
    ticketCreationProcessResult = self.callBatchProcess(
      tenantName=ticketTypeToQueryBack["createTicketTypeResult"]["tenantName"],
      ticketTypeID=ticketTypeToQueryBack["createTicketTypeResult"]["id"],
      foreignKeyList=["testTicket_NOTEXP"],
      foreignKeyDupAction="Skip",
      checkAndParseResponse=True
    )
    NonExpiredTicketForignKey = ticketCreationProcessResult["results"][0]["foreignKey"]
    NonExpiredTicketID = ticketCreationProcessResult["results"][0]["ticketGUID"]

    #6 tickets should have expired, one has not.
    ## Query back the 6 expired
    resultJSON = self.queryForTickets(
      tenantName=setup["tenants"][0]["tenantJSON"]["Name"],
      ticketTypeID=setup["tenants"][0]["ticketTypes"][1]["createTicketTypeResult"]["id"],
      queryString="US_EXPIRED"
    )
    self.assertEqual(len(resultJSON),6,msg="Wrong number of tickets returned")

    #=Query back just the expired ticket
    resultJSON = self.queryForTickets(
      tenantName=setup["tenants"][0]["tenantJSON"]["Name"],
      ticketTypeID=setup["tenants"][0]["ticketTypes"][1]["createTicketTypeResult"]["id"],
      queryString="US_USABLEIFTICKETTYPEISENABLED"
    )
    self.assertEqual(len(resultJSON),1,msg="Wrong number of tickets returned")
    self.assertEqual(resultJSON[0]["id"], NonExpiredTicketID)

    #=Query back just the expired ticket by name and status
    resultJSON = self.queryForTickets(
      tenantName=setup["tenants"][0]["tenantJSON"]["Name"],
      ticketTypeID=setup["tenants"][0]["ticketTypes"][1]["createTicketTypeResult"]["id"],
      queryString="US_USABLEIFTICKETTYPEISENABLED " + NonExpiredTicketForignKey
    )
    self.assertEqual(len(resultJSON),1,msg="Wrong number of tickets returned")
    self.assertEqual(resultJSON[0]["id"], NonExpiredTicketID)

  def test_queryBackSingleDisabledTicket(self):
    testTime1 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime1)

    setup = self.setupTenantsTicketTypesAndTickets()

    ticketTypeToQueryBack = setup["tenants"][0]["ticketTypes"][1]
    ticketToDisable = ticketTypeToQueryBack["ticketCreationProcessResult"]["results"][4]
    disabledTicketID = ticketToDisable["ticketGUID"]
    disabledForeignKey = ticketToDisable["foreignKey"]

    #We need to find the object version number for this ticket
    resultJSON = self.queryForTickets(
      tenantName=setup["tenants"][0]["tenantJSON"]["Name"],
      ticketTypeID=setup["tenants"][0]["ticketTypes"][1]["createTicketTypeResult"]["id"],
      queryString=disabledForeignKey
    )
    self.assertEqual(len(resultJSON),1,msg="Wrong number of tickets returned")
    self.assertEqual(resultJSON[0]["id"], disabledTicketID)
    self.assertEqual(resultJSON[0]["foreignKey"], disabledForeignKey)

    testTime2 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime2)

    disabledObjectVersion = resultJSON[0][object_store_abstraction.RepositoryObjBaseClass.getMetadataElementKey()]["objectVersion"]

    disableResultJSON = self.disableTicket(
      tenantName=ticketTypeToQueryBack["createTicketTypeResult"]["tenantName"],
      ticketTypeID=ticketTypeToQueryBack["createTicketTypeResult"]["id"],
      ticketID=disabledTicketID,
      objectVersionNumber=disabledObjectVersion,
      checkAndParseResponse = True
    )

    expectedDisableResult = {
      "response": "OK",
      "message": "OK",
      "results": [{
        "ticketGUID": disabledTicketID,
        "response": "OK",
        "message": "OK"
      }]
    }
    python_Testing_Utilities.assertObjectsEqual(
      unittestTestCaseClass=self,
      first=disableResultJSON,
      second=expectedDisableResult,
      msg="Disable basic result wrong",
      ignoredRootKeys=["results"]
    )
    self.assertEqual(len(disableResultJSON["results"]),1)
    python_Testing_Utilities.assertObjectsEqual(
      unittestTestCaseClass=self,
      first=disableResultJSON["results"][0],
      second=expectedDisableResult["results"][0],
      msg="Disable result wrong",
      ignoredRootKeys=[]
    )

    #5 tickets should not be disabled, one has is.
    ## Query back the 5 not disabled
    resultJSON = self.queryForTickets(
      tenantName=setup["tenants"][0]["tenantJSON"]["Name"],
      ticketTypeID=setup["tenants"][0]["ticketTypes"][1]["createTicketTypeResult"]["id"],
      queryString="US_USABLEIFTICKETTYPEISENABLED"
    )
    self.assertEqual(len(resultJSON),5,msg="Wrong number of tickets returned")

    #Query back the one disabled
    resultJSON = self.queryForTickets(
      tenantName=setup["tenants"][0]["tenantJSON"]["Name"],
      ticketTypeID=setup["tenants"][0]["ticketTypes"][1]["createTicketTypeResult"]["id"],
      queryString="US_DISABLED"
    )
    self.assertEqual(len(resultJSON),1,msg="Wrong number of tickets returned")
    self.assertEqual(resultJSON[0]["id"], disabledTicketID)
    self.assertEqual(resultJSON[0]["foreignKey"], disabledForeignKey)
