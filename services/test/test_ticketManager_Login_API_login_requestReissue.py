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

class helper(ticketManagerAPICommonUtilsClass):
  def setup(self):
    return self.setupTenantWithTwoTicketTypesAndTickets()

  def requestReissue(
    self,
    tenantName,
    ticketGUID,
    checkAndParseResponse=True
  ):
    result = self.testClient.get(
      self.loginAPIPrefix + '/' + tenantName + '/tickets/' + ticketGUID + '/requestreissue',
      headers={"Origin": TestHelperSuperClass.httpOrigin}
    )
    if not checkAndParseResponse:
      return result
    self.assertEqual(result.status_code, 200)
    return json.loads(result.get_data(as_text=True))

  def loginAPIGetTicket(
    self,
    tenantName,
    ticketGUID,
    checkAndParseResponse = True
  ):
    result = self.testClient.get(
      self.loginAPIPrefix + '/' + tenantName + '/tickets/' + ticketGUID,
      headers={"Origin": TestHelperSuperClass.httpOrigin}
    )
    if not checkAndParseResponse:
      return result
    self.assertEqual(result.status_code, 200)
    return json.loads(result.get_data(as_text=True))

@TestHelperSuperClass.wipd
class ticketManager_LoginAPI_login_API_loginRequestReissue(helper):
  def test_RequestReissueOfExpiredTicket(self):
    setup = self.setup()

    testTime2 = (setup["setupTime"] + datetime.timedelta(hours=int(1 + setup["ticketTypeWithAllowUserCreation"]["issueDuration"])))
    appObj.setTestingDateTime(testTime2)

    requestResultJSON = self.requestReissue(
      tenantName=setup["tenantName"],
      ticketGUID=setup["ticketTypeWithAllowUserCreation"]["tickets"][0]["ticketGUID"]
    )
    self.assertEqual(requestResultJSON["isUsable"],"REISSUEREQUESTED")

    #Check ticket state is now REISSUED when we call a get
    ticketJSON = self.loginAPIGetTicket(
      tenantName=setup["tenantName"],
      ticketGUID=setup["ticketTypeWithAllowUserCreation"]["tickets"][0]["ticketGUID"]
    )
    self.assertEqual(requestResultJSON["isUsable"],"REISSUEREQUESTED")

    qryRes = self.queryForTickets(
      tenantName=setup["tenantName"],
      ticketTypeID=setup["ticketTypeWithAllowUserCreation"]["id"],
      queryString=setup["ticketTypeWithAllowUserCreation"]["tickets"][0]["foreignKey"]
    )
    self.assertEqual(len(qryRes),1)
    self.assertEqual(qryRes[0]["usableState"],"US_REISSUEREQUESTED")
    self.assertEqual(qryRes[0]["reissueRequestedDate"],testTime2.isoformat())

  def test_CanNotReissueValidTicket(self):
    setup = self.setup()

    requestResultRAW = self.requestReissue(
      tenantName=setup["tenantName"],
      ticketGUID=setup["ticketTypeWithAllowUserCreation"]["tickets"][0]["ticketGUID"],
      checkAndParseResponse=False
    )
    self.assertEqual(requestResultRAW.status_code, 400)
    self.assertEqual(json.loads(requestResultRAW.get_data(as_text=True))["message"], "Not possible to renew this ticket")

  def test_CanNotReissueUsedTicket(self):
    setup = self.setup()

    userID="ddddvv"
    InternalAuthUsername="DDDD"
    InternalAuthPassword="Fvfrvd"

    #Auth default user for this tenant
    self.createIntarnalLoginForTenant(
      tenantName=setup["tenantName"],
      userID=userID,
      InternalAuthUsername=InternalAuthUsername,
      InternalAuthPassword=InternalAuthPassword
    )

    #Use the ticket
    loginRespData = self.loginAsUser(
      tenant=setup["tenantName"],
      authProviderDICT=self.getTenantInternalAuthProvDict(tenant=setup["tenantName"]),
      username=InternalAuthUsername,
      password=InternalAuthPassword,
      ticketToPass=setup["ticketTypeWithAllowUserCreation"]["tickets"][0]["ticketGUID"]
    )

    testTime2 = (setup["setupTime"] + datetime.timedelta(hours=int(1 + setup["ticketTypeWithAllowUserCreation"]["issueDuration"])))
    appObj.setTestingDateTime(testTime2)

    requestResultRAW = self.requestReissue(
      tenantName=setup["tenantName"],
      ticketGUID=setup["ticketTypeWithAllowUserCreation"]["tickets"][0]["ticketGUID"],
      checkAndParseResponse = False
    )
    self.assertEqual(requestResultRAW.status_code, 400)
    self.assertEqual(json.loads(requestResultRAW.get_data(as_text=True))["message"], "Not possible to renew this ticket")

