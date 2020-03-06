import TestHelperSuperClass
import copy
import ticketManagerTestCommon
import constants
import json

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
