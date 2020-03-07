import TestHelperSuperClass
from ticketManager__Common_API import ticketManagerAPICommonUtilsClass
import copy
import python_Testing_Utilities

class helper(ticketManagerAPICommonUtilsClass):
  def setupTenantsTicketTypesAndTickets(self, tenantData=TestHelperSuperClass.tenantWithNoAuthProviders):
    tenants = []
    for tenantIdx in range(1,10):
      tenantData2Use = copy.deepcopy(tenantData)
      tenantData2Use["Name"] = "TestTenant_" + "{:03d}".format(tenantIdx)
      tenantJSON = self.createTenantForTesting(tenantData2Use)

      ticketTypes = []
      for ticketTypesIdx in range(1, 3):
        createTicketTypeResult = self.createTicketType(tenantJSON["Name"], overrideName="TestTicketType_" + "{:03d}".format(ticketTypesIdx))

        ticketCreationProcessResult = self.callBatchProcess(
          tenantName=tenantJSON["Name"],
          ticketTypeID=createTicketTypeResult["id"],
          foreignKeyList=["testTicket_001", "testTicket_002", "testTicket_003", "testTicket_004", "testTicket_005", "testTicket_006"],
          foreignKeyDupAction="Skip",
          checkAndParseResponse=True
        )
        ticketTypes.append({
          "createTicketTypeResult": createTicketTypeResult,
          "ticketCreationProcessResult": ticketCreationProcessResult
        })

      tenants.append({
        "tanantJSON": tenantJSON,
        "ticketTypes": ticketTypes
      })

    return {
      "tenants": tenants
    }

@TestHelperSuperClass.wipd
class ticketManager_ViewTickets_API(helper):
  def test_QueryBackAllTicketsOfType(self):
    setup = self.setupTenantsTicketTypesAndTickets()

    resultJSON = self.queryForTickets(tenantName=setup["tenants"][0]["tanantJSON"]["Name"], ticketTypeID=setup["tenants"][0]["ticketTypes"][1]["createTicketTypeResult"]["id"], queryString=None)
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
      tenantName=setup["tenants"][0]["tanantJSON"]["Name"],
      ticketTypeID=setup["tenants"][0]["ticketTypes"][1]["createTicketTypeResult"]["id"],
      queryString=ticketToQueryBack["foreignKey"]
    )
    self.assertEqual(len(resultJSON),1,msg="Wrong number of tickets returned")

    self.assertEqual(resultJSON[0]["id"], ticketToQueryBack["ticketGUID"])
    self.assertEqual(resultJSON[0]["foreignKey"], ticketToQueryBack["foreignKey"])



