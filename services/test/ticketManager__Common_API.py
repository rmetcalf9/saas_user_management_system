import TestHelperSuperClass
import copy
import ticketManagerTestCommon
import constants
import json
from urllib.parse import urlencode, quote_plus

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
        "tenantJSON": tenantJSON,
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

