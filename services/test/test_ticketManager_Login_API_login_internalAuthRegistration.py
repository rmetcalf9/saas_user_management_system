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
    return self.setupTenantWithTwoTicketTypesAndTickets()

#@TestHelperSuperClass.wipd
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

  def test_CanNotUseTicketTwice(self):
    setup = self.setup()

    userName1 = "testSetUserName"
    password1 = "delkjgn4rflkjwned"
    userName2 = "testSetUserName22"
    password2 = "delkjgn4rflkjwned22"

    expectedRoles = [constants.DefaultHasAccountRole] + ticketManagerTestCommon.validTicketTypeDict["roles"]

    testDateTime2 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testDateTime2)
    _ = self.registerInternalUser(
      setup["tenantName"],
      userName1,
      password1,
      self.getTenantInternalAuthProvDict(tenant=setup["tenantName"]),
      ticketGUID=setup["ticketTypeWithAllowUserCreation"]["tickets"][0]["ticketGUID"]
    )
    registerResultJSON2 = self.registerInternalUser(
      setup["tenantName"],
      userName2,
      password2,
      self.getTenantInternalAuthProvDict(tenant=setup["tenantName"]),
      ticketGUID=setup["ticketTypeWithAllowUserCreation"]["tickets"][0]["ticketGUID"],
      expectedResults=[400]
    )
    self.assertEqual(registerResultJSON2["message"],"Ticket not usable")

  def test_InternalAuthRegisterWithInvalidGUIDTicketFails(self):
    setup = self.setup()

    userName = "testSetUserName"
    password = "delkjgn4rflkjwned"

    testDateTime2 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testDateTime2)
    registerResultJSON = self.registerInternalUser(
      setup["tenantName"],
      userName,
      password,
      self.getTenantInternalAuthProvDict(tenant=setup["tenantName"]),
      ticketGUID="INVALIDTICKETID",
      expectedResults=[400]
    )
    self.assertEqual(registerResultJSON["message"],"Invalid Ticket")

  def test_InternalAuthRegisterWithExpiredTicketFails(self):
    #Auth provider has no allow user creatoin. Ticket has
    setup = self.setup()

    userName = "testSetUserName"
    password = "delkjgn4rflkjwned"

    testDateTime2 = datetime.datetime.now(pytz.timezone("UTC")) + datetime.timedelta(hours=1 + int(setup["ticketTypeWithAllowUserCreation"]["issueDuration"]))
    appObj.setTestingDateTime(testDateTime2)
    registerResultJSON = self.registerInternalUser(
      setup["tenantName"],
      userName,
      password,
      self.getTenantInternalAuthProvDict(tenant=setup["tenantName"]),
      ticketGUID=setup["ticketTypeWithAllowUserCreation"]["tickets"][0]["ticketGUID"]
      ,expectedResults=[400]
    )
    self.assertEqual(registerResultJSON["message"],"Ticket not usable")

  def test_InternalAuthRegisterWithTicketTypeWithNoUserCreationFails(self):
    #Auth provider has no allow user creatoin. Ticket has
    setup = self.setup()

    userName = "testSetUserName"
    password = "delkjgn4rflkjwned"

    registerResultJSON = self.registerInternalUser(
      setup["tenantName"],
      userName,
      password,
      self.getTenantInternalAuthProvDict(tenant=setup["tenantName"]),
      ticketGUID=setup["ticketTypeWithOUTAllowUserCreation"]["tickets"][0]["ticketGUID"]
      ,expectedResults=[401]
    )
    self.assertEqual(registerResultJSON["message"],"User Creation Not Allowed")