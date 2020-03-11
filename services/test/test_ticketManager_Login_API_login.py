import TestHelperSuperClass
from ticketManager__Common_API import ticketManagerAPICommonUtilsClass
import datetime
import pytz
from appObj import appObj
import object_store_abstraction
import copy
import constants
import ticketManagerTestCommon

twoRoleList = [ "TestRoleA", "TestRoleB" ]

class helper(ticketManagerAPICommonUtilsClass):
  def setDisabledForTicket(self, setup, tenant, ticketType, ticket):
    #Ticket object version is not in initial setup so needs to be queried for
    QueryRESJSON = self.queryForTickets(
      tenantName=setup["tenants"][tenant]["tenantJSON"]["Name"],
      ticketTypeID=setup["tenants"][tenant]["ticketTypes"][ticketType]["createTicketTypeResult"]["id"],
      queryString=setup["tenants"][tenant]["ticketTypes"][ticketType]["ticketCreationProcessResult"]["results"][ticket]["foreignKey"]
    )
    self.assertEqual(len(QueryRESJSON), 1)
    resJSON = self.disableTicket(
      tenantName=setup["tenants"][tenant]["tenantJSON"]["Name"],
      ticketTypeID=setup["tenants"][tenant]["ticketTypes"][ticketType]["createTicketTypeResult"]["id"],
      ticketID=setup["tenants"][tenant]["ticketTypes"][ticketType]["ticketCreationProcessResult"]["results"][ticket]["ticketGUID"],
      objectVersionNumber=QueryRESJSON[0][object_store_abstraction.RepositoryObjBaseClass.getMetadataElementKey()]["objectVersion"],
      checkAndParseResponse=True
    )
    setup["tenants"][tenant]["ticketTypes"][ticketType]["createTicketTypeResult"] = resJSON
    return setup

  def updateTicketTypeFromSetup(self, setup, tenant, ticketType, updFN):
    newDict = updFN(copy.deepcopy(setup["tenants"][tenant]["ticketTypes"][ticketType]["createTicketTypeResult"]))
    setup["tenants"][tenant]["ticketTypes"][ticketType]["createTicketTypeResult"] = self.updateTicketType(
      ticketTypeID=setup["tenants"][tenant]["ticketTypes"][ticketType]["createTicketTypeResult"]["id"],
      ticketTypeTenant=setup["tenants"][tenant]["tenantJSON"]["Name"],
      newDict=newDict,
      checkAndParseResponse=True
    )
    return setup

  def setRolesForTicketType(self, setup, tenant, ticketType, roles):
    def updFN(oldTicketTypeObj):
      oldTicketTypeObj["roles"] = roles
      return oldTicketTypeObj
    return self.updateTicketTypeFromSetup(setup, tenant, ticketType, updFN)

  def setAllowUserCreationForTicketType(self, setup, tenant, ticketType, allowUserCreation):
    def updFN(oldTicketTypeObj):
      oldTicketTypeObj["allowUserCreation"] = allowUserCreation
      return oldTicketTypeObj
    return self.updateTicketTypeFromSetup(setup, tenant, ticketType, updFN)

  def setEnabledForTicketType(self, setup, tenant, ticketType, enabled):
    def updFN(oldTicketTypeObj):
      oldTicketTypeObj["enabled"] = enabled
      return oldTicketTypeObj
    return self.updateTicketTypeFromSetup(setup, tenant, ticketType, updFN)

  def mainSetup(self):
    testTime1 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime1)
    setup = self.setupTenantsTicketTypesAndTickets()

    #tenant 0, ticketType 0, result 0 - ticket with one role
    #tenant 0, ticketType 0, result 1 - ticket has been disabled
    #tenant 0, ticketType 1, result 0 - ticket with two roles
    #tenant 0, ticketType 2, result 0 - ticket type usercreation is false
    #tenant 1, ticketType 0, result 0 - ticket type is disabled

    setup = self.setDisabledForTicket(setup=setup, tenant=0, ticketType=0, ticket=1)
    setup = self.setRolesForTicketType(setup=setup, tenant=0, ticketType=1, roles=twoRoleList)
    setup = self.setAllowUserCreationForTicketType(setup=setup, tenant=1, ticketType=0, allowUserCreation=False)
    setup = self.setEnabledForTicketType(setup=setup, tenant=1, ticketType=1, enabled=False)

    def getTicketInfo(tenant, ticketType, ticket):
      return {
        "tenantName": setup["tenants"][tenant]["tenantJSON"]["Name"],
        "tenantLoginInfo": setup["tenants"][tenant]["tenantLoginInfo"],
        "ticketGUID": setup["tenants"][tenant]["ticketTypes"][ticketType]["ticketCreationProcessResult"]["results"][ticket]["ticketGUID"]
      }

    return {
      "setuptime": testTime1,
      "ticketWithOneRoleAndAllowUserCreationTrue": getTicketInfo(tenant=0, ticketType=0, ticket=0),
      "ticketOnDisabledTicketType": getTicketInfo(tenant=0, ticketType=0, ticket=1),
      "ticketWithTwoRolesAndAllowUserCreationTrue": getTicketInfo(tenant=1, ticketType=0, ticket=0),
      "ticketWithOneRoleAndAllowUserCreationFalse": getTicketInfo(tenant=1, ticketType=1, ticket=0)
    }

@TestHelperSuperClass.wipd
class ticketManager_LoginAPI_login_API(helper):
  def test_ExistingUserUsingTicket(self):
    setup = self.mainSetup()
    ticketToUse = setup["ticketWithOneRoleAndAllowUserCreationTrue"]
    loginRespData = self.loginAsUser(
      tenant=ticketToUse["tenantName"],
      authProviderDICT=self.getTenantInternalAuthProvDict(tenant=ticketToUse["tenantName"]),
      username=ticketToUse["tenantLoginInfo"]["InternalAuthUsername"],
      password=ticketToUse["tenantLoginInfo"]["InternalAuthPassword"],
      ticketToPass=ticketToUse["ticketGUID"]
    )
    self.assertEqual(loginRespData["ThisTenantRoles"],[constants.DefaultHasAccountRole] + ticketManagerTestCommon.validTicketTypeDict["roles"])

    #Login again without ticket and make sure role sticks
    loginRespData2 = self.loginAsUser(
      tenant=ticketToUse["tenantName"],
      authProviderDICT=self.getTenantInternalAuthProvDict(tenant=ticketToUse["tenantName"]),
      username=ticketToUse["tenantLoginInfo"]["InternalAuthUsername"],
      password=ticketToUse["tenantLoginInfo"]["InternalAuthPassword"],
      ticketToPass=None
    )
    self.assertEqual(loginRespData2["ThisTenantRoles"],[constants.DefaultHasAccountRole] + ticketManagerTestCommon.validTicketTypeDict["roles"])

#  def test_ExistingUserUsingTicketTwoRoles(self):
    #self.assertEqual(loginRespData["ThisTenantRoles"],[constants.DefaultHasAccountRole] + twoRoleList)

#  def test_ExistingUserUsingTicketTwoRolesAlreadyGranted(self):
    #self.assertEqual(loginRespData["ThisTenantRoles"],[constants.DefaultHasAccountRole] + twoRoleList)

#  def test_ExistingUserUsingTicketTwoRolesOneAlreadyGrantedOne(self):
    #self.assertEqual(loginRespData["ThisTenantRoles"],[constants.DefaultHasAccountRole] + twoRoleList)


#  def test_NewUserUsingTicket(self):

# def test_NewUserUsingTicketFailsBecauseAuthIsNone(self):

#def test_ticketTypeIsDisabled

#def test_cantUseTicketTwice

#def test_cantUseDisabledTicket

#def test_cantUseExpiredTicket

#def test_ExistingUserWithCompletlyInvalidTicket

#def test_NewUserWithCompletlyInvalidTicket

#TODO Think about how a person with mutiple users uses a ticket
