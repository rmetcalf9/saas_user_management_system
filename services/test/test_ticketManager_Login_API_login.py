import TestHelperSuperClass
from ticketManager__Common_API import ticketManagerAPICommonUtilsClass
import datetime
import pytz
from appObj import appObj
import object_store_abstraction
import copy
import constants
import ticketManagerTestCommon
import json

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
    #print("O", setup["tenants"][tenant]["ticketTypes"][ticketType]["ticketCreationProcessResult"])
    #print("R", resJSON)
    #self.assertTrue(False)
    #DO not update setup because
    #  1. create process has no fields that are chaging
    #  2. I would have to place it in exact sopt in array
    return setup

  def updateTicketTypeFromSetup(self, setup, tenant, ticketType, updFN):
    newDict = updFN(copy.deepcopy(setup["tenants"][tenant]["ticketTypes"][ticketType]["createTicketTypeResult"]))
    res = self.updateTicketType(
      ticketTypeID=setup["tenants"][tenant]["ticketTypes"][ticketType]["createTicketTypeResult"]["id"],
      ticketTypeTenant=setup["tenants"][tenant]["tenantJSON"]["Name"],
      newDict=newDict,
      checkAndParseResponse=True
    )
    setup["tenants"][tenant]["ticketTypes"][ticketType]["createTicketTypeResult"] = res
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

    setup = self.setDisabledForTicket(setup=setup, tenant=0, ticketType=0, ticket=1)
    setup = self.setRolesForTicketType(setup=setup, tenant=0, ticketType=1, roles=twoRoleList)
    setup = self.setAllowUserCreationForTicketType(setup=setup, tenant=1, ticketType=0, allowUserCreation=False)
    setup = self.setEnabledForTicketType(setup=setup, tenant=1, ticketType=1, enabled=False)

    def getTicketInfo(tenant, ticketType, ticket):
      return {
        "tenantName": setup["tenants"][tenant]["tenantJSON"]["Name"],
        "tenantLoginInfo": setup["tenants"][tenant]["tenantLoginInfo"],
        "ticketGUID": setup["tenants"][tenant]["ticketTypes"][ticketType]["ticketCreationProcessResult"]["results"][ticket]["ticketGUID"],
        "foreignKey": setup["tenants"][tenant]["ticketTypes"][ticketType]["ticketCreationProcessResult"]["results"][ticket]["foreignKey"],
        "ticketTypeID": setup["tenants"][tenant]["ticketTypes"][ticketType]["createTicketTypeResult"]["id"]
        #,"ticketType": setup["tenants"][tenant]["ticketTypes"][ticketType]["createTicketTypeResult"]
      }

    return {
      "setuptime": testTime1,
      "ticketWithOneRoleAndAllowUserCreationTrue": getTicketInfo(tenant=0, ticketType=0, ticket=0),
      "ticketOnDisabledTicketType": getTicketInfo(tenant=0, ticketType=0, ticket=1),
      "ticketWithTwoRolesAndAllowUserCreationTrue": getTicketInfo(tenant=0, ticketType=1, ticket=0),
      "ticketWithOneRoleAndAllowUserCreationFalse": getTicketInfo(tenant=1, ticketType=1, ticket=0)
    }

  def assertTicketUsed(self,
    tenantName,
    foreignKey,
    ticketGUID,
    ticketTypeID,
    userID,
    timeUsed
  ):
    #There is no function to return full data on an individual ticket GUID (Only login)
    # so doing full search on foreign key, only works where there is only one ticket
    ###print("ticketTypeID:", ticketTypeID)
    qryRes = self.queryForTickets(tenantName=tenantName, ticketTypeID=ticketTypeID, queryString=foreignKey)
    self.assertEqual(len(qryRes), 1)
    self.assertEqual(qryRes[0]["id"], ticketGUID)
    self.assertEqual(qryRes[0]["typeGUID"], ticketTypeID)
    self.assertEqual(qryRes[0]["useWithUserID"], userID, msg="Was not marked with user that used ticket")
    self.assertEqual(qryRes[0]["usedDate"], timeUsed.isoformat())
    self.assertEqual(qryRes[0]["usableState"], "US_ALREADYUSED")

@TestHelperSuperClass.wipd
class ticketManager_LoginAPI_login_API(helper):
  def test_ExistingUserUsingTicket(self):
    setup = self.mainSetup()
    ticketToUse = setup["ticketWithOneRoleAndAllowUserCreationTrue"]
    testTime1 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime1)
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

    #Make sure this ticket has the info recorded against it to show it has been used
    self.assertTicketUsed(
      tenantName=ticketToUse["tenantName"],
      foreignKey=ticketToUse["foreignKey"],
      ticketGUID=ticketToUse["ticketGUID"],
      ticketTypeID=ticketToUse["ticketTypeID"],
      userID=ticketToUse["tenantLoginInfo"]["userID"],
      timeUsed=testTime1
    )

  def test_ExistingUserUsingTicketTwoRoles(self):
    setup = self.mainSetup()
    ticketToUse = setup["ticketWithTwoRolesAndAllowUserCreationTrue"]
    testTime1 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime1)
    loginRespData = self.loginAsUser(
      tenant=ticketToUse["tenantName"],
      authProviderDICT=self.getTenantInternalAuthProvDict(tenant=ticketToUse["tenantName"]),
      username=ticketToUse["tenantLoginInfo"]["InternalAuthUsername"],
      password=ticketToUse["tenantLoginInfo"]["InternalAuthPassword"],
      ticketToPass=ticketToUse["ticketGUID"]
    )
    self.assertEqual(loginRespData["ThisTenantRoles"],[constants.DefaultHasAccountRole] + twoRoleList)

    #Login again without ticket and make sure role sticks
    loginRespData2 = self.loginAsUser(
      tenant=ticketToUse["tenantName"],
      authProviderDICT=self.getTenantInternalAuthProvDict(tenant=ticketToUse["tenantName"]),
      username=ticketToUse["tenantLoginInfo"]["InternalAuthUsername"],
      password=ticketToUse["tenantLoginInfo"]["InternalAuthPassword"],
      ticketToPass=None
    )
    self.assertEqual(loginRespData["ThisTenantRoles"],[constants.DefaultHasAccountRole] + twoRoleList)

    #Make sure this ticket has the info recorded against it to show it has been used
    self.assertTicketUsed(
      tenantName=ticketToUse["tenantName"],
      foreignKey=ticketToUse["foreignKey"],
      ticketGUID=ticketToUse["ticketGUID"],
      ticketTypeID=ticketToUse["ticketTypeID"],
      userID=ticketToUse["tenantLoginInfo"]["userID"],
      timeUsed=testTime1
    )

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
