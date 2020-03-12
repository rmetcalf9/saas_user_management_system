#Tests for internal auth registration
import TestHelperSuperClass
from ticketManager__Common_API import ticketManagerAPICommonUtilsClass
import ticketManagerTestCommon
import datetime
import pytz
from appObj import appObj
import json
import constants

class helper(ticketManagerAPICommonUtilsClass):
  def setup(self):
    testDateTime = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testDateTime)

    tenantDict = self.createTenantWithAuthProvider(
      TestHelperSuperClass.tenantWithNoAuthProviders,
      True,
      TestHelperSuperClass.sampleInternalAuthProv001_CREATE #allow user creation is false
    )
    ticketTypeWithAllowUserCreation = self.createTicketType(
      tenantDict["Name"],
      overrideName="TestTicketTypeWithAllowUserCreation"
    )
    AllowUserCreationTickets = self.callBatchProcess(
      tenantName=tenantDict["Name"],
      ticketTypeID=ticketTypeWithAllowUserCreation["id"],
      foreignKeyList=["testTicket_001"],
      foreignKeyDupAction="Skip",
      checkAndParseResponse=True
    )
    ticketTypeWithOUTAllowUserCreation = self.createTicketType(
      tenantDict["Name"],
      overrideName="TestTicketTypeWithAllowUserCreation"
    )
    ticketTypeWithOUTAllowUserCreation["allowUserCreation"] = False
    ticketTypeWithOUTAllowUserCreation = self.updateTicketType(
      ticketTypeID=ticketTypeWithOUTAllowUserCreation["id"],
      ticketTypeTenant=tenantDict["Name"],
      newDict=ticketTypeWithOUTAllowUserCreation,
      checkAndParseResponse=True
    )
    DISAllowUserCreationTickets = self.callBatchProcess(
      tenantName=tenantDict["Name"],
      ticketTypeID=ticketTypeWithOUTAllowUserCreation["id"],
      foreignKeyList=["testTicket_001_NOCREATION"],
      foreignKeyDupAction="Skip",
      checkAndParseResponse=True
    )

    return {
      "setupTime": testDateTime,
      "tenantName": tenantDict["Name"],
      "ticketTypeWithAllowUserCreation": {
        "id": ticketTypeWithAllowUserCreation["id"],
        "tickets": AllowUserCreationTickets["results"]
      },
      "ticketTypeWithOUTAllowUserCreation": {
        "id": ticketTypeWithOUTAllowUserCreation["id"],
        "tickets": DISAllowUserCreationTickets["results"]
      }
    }

@TestHelperSuperClass.wipd
class ticketManager_LoginAPI_login_API_internalAuthRegistration(helper):
  def test_registerInternalAuthWithTicket(self):
    #Auth provider has no allow user creatoin. Ticket has
    setup = self.setup()

    userName = "testSetUserName"
    password = "delkjgn4rflkjwned"

    expectedRoles = [constants.DefaultHasAccountRole] + ticketManagerTestCommon.validTicketTypeDict["roles"]

    testDateTime2 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testDateTime2)
    registerResultJSON = self.registerInternalUser(
      setup["tenantName"],
      userName,
      password,
      self.getTenantInternalAuthProvDict(tenant=setup["tenantName"]),
      ticketGUID=setup["ticketTypeWithAllowUserCreation"]["tickets"][0]["ticketGUID"]
    )
    thisTenantRoles = None
    for dict in registerResultJSON["TenantRoles"]:
      if dict["TenantName"]==setup["tenantName"]:
        thisTenantRoles=dict
    self.assertEqual(thisTenantRoles["ThisTenantRoles"], expectedRoles)

    loginRespData2 = self.loginAsUser(
      tenant=setup["tenantName"],
      authProviderDICT=self.getTenantInternalAuthProvDict(tenant=setup["tenantName"]),
      username=userName,
      password=password,
      ticketToPass=None
    )
    self.assertEqual(loginRespData2["ThisTenantRoles"],expectedRoles,)

    self.assertTicketUsed(
      tenantName=setup["tenantName"],
      foreignKey=setup["ticketTypeWithAllowUserCreation"]["tickets"][0]["foreignKey"],
      ticketGUID=setup["ticketTypeWithAllowUserCreation"]["tickets"][0]["ticketGUID"],
      ticketTypeID=setup["ticketTypeWithAllowUserCreation"]["id"],
      userID=registerResultJSON["UserID"],
      timeUsed=testDateTime2
    )

  #def test_CanNotUseTicketTwice(self):

  #def test_InternalAuthRegisterWithInvalidGUIDTicketFails(self):
  #  pass

  #def test_InternalAuthRegisterWithExpiredTicketFails(self):

  #def test_InternalAuthRegisterWithTicketTypeWithNoUserCreationFails(self):
