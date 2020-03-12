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

#New Internal auth registratin tested inside test_ticketManager_Login_API_login_internalAuthRegistration
#Using ticket with Google tested inside test_authProviders_Google.py

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
        "ticketTypeID": setup["tenants"][tenant]["ticketTypes"][ticketType]["createTicketTypeResult"]["id"],
        "ticketTypeIssueDuration": setup["tenants"][tenant]["ticketTypes"][ticketType]["createTicketTypeResult"]["issueDuration"]
        #,"ticketType": setup["tenants"][tenant]["ticketTypes"][ticketType]["createTicketTypeResult"]
      }

    return {
      "setuptime": testTime1,
      "ticketWithOneRoleAndAllowUserCreationTrue": getTicketInfo(tenant=0, ticketType=0, ticket=0),
      "disabledTicket": getTicketInfo(tenant=0, ticketType=0, ticket=1),
      "ticketOnDisabledTicketType": getTicketInfo(tenant=1, ticketType=1, ticket=0),
      "ticketWithTwoRolesAndAllowUserCreationTrue": getTicketInfo(tenant=0, ticketType=1, ticket=0),
      "ticketWithOneRoleAndAllowUserCreationFalse": getTicketInfo(tenant=1, ticketType=1, ticket=0)
    }


#@TestHelperSuperClass.wipd
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

  def test_ticketTypeIsDisabled(self):
    setup = self.mainSetup()
    ticketToUse = setup["ticketOnDisabledTicketType"]
    loginRespData = self.loginAsUser(
      tenant=ticketToUse["tenantName"],
      authProviderDICT=self.getTenantInternalAuthProvDict(tenant=ticketToUse["tenantName"]),
      username=ticketToUse["tenantLoginInfo"]["InternalAuthUsername"],
      password=ticketToUse["tenantLoginInfo"]["InternalAuthPassword"],
      ticketToPass=ticketToUse["ticketGUID"],
      expectedResults=[400]
    )
    self.assertEqual(loginRespData["message"],"Ticket not usable")

  def test_cantUseTicketTwice(self):
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
      ticketToPass=ticketToUse["ticketGUID"],
      expectedResults=[400]
    )
    self.assertEqual(loginRespData2["message"],"Ticket not usable")

  def test_cantUseDisabledTicket(self):
    setup = self.mainSetup()
    ticketToUse = setup["disabledTicket"]
    loginRespData = self.loginAsUser(
      tenant=ticketToUse["tenantName"],
      authProviderDICT=self.getTenantInternalAuthProvDict(tenant=ticketToUse["tenantName"]),
      username=ticketToUse["tenantLoginInfo"]["InternalAuthUsername"],
      password=ticketToUse["tenantLoginInfo"]["InternalAuthPassword"],
      ticketToPass=ticketToUse["ticketGUID"],
      expectedResults=[400]
    )
    self.assertEqual(loginRespData["message"],"Ticket not usable")

  def test_cantUseExpiredTicket(self):
    setup = self.mainSetup()
    ticketToUse = setup["ticketWithOneRoleAndAllowUserCreationTrue"]
    testTime1 = datetime.datetime.now(pytz.timezone("UTC")) + datetime.timedelta(hours=int(1 + ticketToUse["ticketTypeIssueDuration"]))
    appObj.setTestingDateTime(testTime1)
    loginRespData = self.loginAsUser(
      tenant=ticketToUse["tenantName"],
      authProviderDICT=self.getTenantInternalAuthProvDict(tenant=ticketToUse["tenantName"]),
      username=ticketToUse["tenantLoginInfo"]["InternalAuthUsername"],
      password=ticketToUse["tenantLoginInfo"]["InternalAuthPassword"],
      ticketToPass=ticketToUse["ticketGUID"],
      expectedResults=[400]
    )
    self.assertEqual(loginRespData["message"],"Ticket not usable")


  def test_ExistingUserWithCompletlyInvalidTicketGUID(self):
    setup = self.mainSetup()
    ticketToUse = setup["ticketWithTwoRolesAndAllowUserCreationTrue"]
    loginRespData = self.loginAsUser(
      tenant=ticketToUse["tenantName"],
      authProviderDICT=self.getTenantInternalAuthProvDict(tenant=ticketToUse["tenantName"]),
      username=ticketToUse["tenantLoginInfo"]["InternalAuthUsername"],
      password=ticketToUse["tenantLoginInfo"]["InternalAuthPassword"],
      ticketToPass="BADTICKETGUID",
      expectedResults=[400]
    )
    self.assertEqual(loginRespData["message"],"Invalid Ticket")

  #def test_NewUserWithCompletlyInvalidTicketGUID(self):
    #Test only applies to Google auth as internal auth users must use register API
    # setup = self.mainSetup()
    # ticketToUse = setup["ticketWithTwoRolesAndAllowUserCreationTrue"]
    # loginRespData = self.loginAsUser(
    #   tenant=ticketToUse["tenantName"],
    #   authProviderDICT=self.getTenantInternalAuthProvDict(tenant=ticketToUse["tenantName"]),
    #   username="??",
    #   password="??",
    #   ticketToPass="BADTICKETGUID",
    #   expectedResults=[400]
    # )
    # self.assertEqual(loginRespData["message"],"Invalid Ticket")

#  def test_ExistingUserUsingTicketTwoRolesAlreadyGranted(self):
    #self.assertEqual(loginRespData["ThisTenantRoles"],[constants.DefaultHasAccountRole] + twoRoleList)

#  def test_ExistingUserUsingTicketTwoRolesOneAlreadyGrantedOne(self):
    #self.assertEqual(loginRespData["ThisTenantRoles"],[constants.DefaultHasAccountRole] + twoRoleList)

#  def test_NewUserUsingTicket(self):

# def test_NewUserUsingTicketFailsBecauseAllowUserCreationIsFalse(self):



#Add tests where users have account on another tenant
#Make sure this doesn't lead to allow user creation loophole on either tenant

#TODO Think about how a person with mutiple users uses a ticket
