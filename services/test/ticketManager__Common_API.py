import TestHelperSuperClass
import copy
import ticketManagerTestCommon
import constants
import json
from urllib.parse import urlencode, quote_plus
import datetime
import pytz
from appObj import appObj

class ticketManagerAPICommonUtilsClass(TestHelperSuperClass.testHelperAPIClient):
  def createTicketType(self, tenantTypesTenant, overrideName=None):
    jsonData = copy.deepcopy(ticketManagerTestCommon.validTicketTypeDict)
    if overrideName is not None:
      jsonData["ticketTypeName"] = overrideName
    jsonData["tenantName"] = tenantTypesTenant
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants/' + tenantTypesTenant + '/tickettypes',
      headers={constants.jwtHeaderName: self.getNormalJWTToken()},
      data=json.dumps(jsonData),
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 201, msg="Err: " + result.get_data(as_text=True))
    return json.loads(result.get_data(as_text=True))

  def callBatchProcess(
      self,
      tenantName,
      ticketTypeID,
      foreignKeyList,
      foreignKeyDupAction,
      checkAndParseResponse = True
  ):
    postData = {
      "foreignKeyDupAction": foreignKeyDupAction,
      "foreignKeyList": foreignKeyList
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

  def queryForTickets(self, tenantName, ticketTypeID, queryString):
    params = {
      "query": queryString
    }
    postfix = ""
    if queryString is not None:
      postfix = "?" + urlencode(params, quote_via=quote_plus)
    url = self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants/' + tenantName + '/tickettypes/' + ticketTypeID + '/tickets' + postfix
    result2 = self.testClient.get(
      url,
      headers={constants.jwtHeaderName: self.getNormalJWTToken()},
      data=None,
      content_type='application/json'
    )
    self.assertEqual(result2.status_code, 200)
    ResultJSON = json.loads(result2.get_data(as_text=True))

    return ResultJSON["result"]

  def disableTicket(self,
    tenantName,
    ticketTypeID,
    ticketID,
    objectVersionNumber,
    checkAndParseResponse = True
  ):
    postData = {
      "tickets": [{
        "ticketGUID": ticketID,
        "objectVersion": objectVersionNumber
      }]
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants/' + tenantName + '/tickettypes/' + ticketTypeID + '/tickets/disablebatch',
      headers={constants.jwtHeaderName: self.getNormalJWTToken()},
      data=json.dumps(postData),
      content_type='application/json'
    )
    if not checkAndParseResponse:
      return result
    self.assertEqual(result.status_code, 200, msg="Err: " + result.get_data(as_text=True))
    return json.loads(result.get_data(as_text=True))

  def setupTenantsTicketTypesAndTickets(self, tenantData=TestHelperSuperClass.tenantWithNoAuthProviders):
    tenants = []
    for tenantIdx in range(1,10):
      tenantData2Use = copy.deepcopy(tenantData)
      tenantData2Use["Name"] = "TestTenant_" + "{:03d}".format(tenantIdx)
      tenantJSON = self.createTenantForTestingWithMutipleAuthProviders(tenantData2Use, [TestHelperSuperClass.sampleInternalAuthProv001_CREATE])

      userID = tenantJSON["Name"] + "_USRID"
      InternalAuthUsername = tenantJSON["Name"] + "_USR"
      InternalAuthPassword = tenantJSON["Name"] + "_USRPASS"

      self.createIntarnalLoginForTenant(
        tenantName=tenantJSON["Name"],
        userID=userID,
        InternalAuthUsername=InternalAuthUsername,
        InternalAuthPassword=InternalAuthPassword
      )

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
        "tenantJSON": tenantJSON,
        "tenantLoginInfo": {
          "userID": userID,
          "InternalAuthUsername": InternalAuthUsername,
          "InternalAuthPassword": InternalAuthPassword
        },
        "ticketTypes": ticketTypes
      })

    return {
      "tenants": tenants
    }

  def updateTicketType(self, ticketTypeID, ticketTypeTenant, newDict, checkAndParseResponse=True):
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants/' + ticketTypeTenant + '/tickettypes/' + ticketTypeID,
      headers={constants.jwtHeaderName: self.getNormalJWTToken()},
      data=json.dumps(newDict),
      content_type='application/json'
    )
    if not checkAndParseResponse:
      return result
    self.assertEqual(result.status_code, 202, msg="Err: " + result.get_data(as_text=True))
    return json.loads(result.get_data(as_text=True))


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

  def setupTenantWithTwoTicketTypesAndTickets(self, authProv=TestHelperSuperClass.sampleInternalAuthProv001_CREATE):
    testDateTime = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testDateTime)

    tenantDict = self.createTenantWithAuthProvider(
      tenantBase=TestHelperSuperClass.tenantWithNoAuthProviders,
      tenantUserCreation=False,
      authProvDict=authProv
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
        "issueDuration": ticketTypeWithOUTAllowUserCreation["issueDuration"],
        "tickets": AllowUserCreationTickets["results"]
      },
      "ticketTypeWithOUTAllowUserCreation": {
        "id": ticketTypeWithOUTAllowUserCreation["id"],
        "issueDuration": ticketTypeWithOUTAllowUserCreation["issueDuration"],
        "tickets": DISAllowUserCreationTickets["results"]
      }
    }