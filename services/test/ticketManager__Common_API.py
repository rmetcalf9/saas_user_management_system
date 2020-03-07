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
