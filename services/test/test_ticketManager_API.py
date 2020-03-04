import TestHelperSuperClass
import ticketManagerTestCommon
import constants
import json
import copy
import object_store_abstraction
import python_Testing_Utilities
import datetime
import pytz
from appObj import appObj

class helper(TestHelperSuperClass.testHelperAPIClient):
  pass

@TestHelperSuperClass.wipd
class ticketManager_helpers(helper):
  def test_createValidTicketType(self):
    testTime = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime)
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants/' + constants.masterTenantName + '/tickettypes',
      headers={ constants.jwtHeaderName: self.getNormalJWTToken()},
      data=json.dumps(ticketManagerTestCommon.validTicketTypeDict),
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 201)
    resultJSON = json.loads(result.get_data(as_text=True))

    expectedResult = copy.deepcopy(ticketManagerTestCommon.validTicketTypeDict)
    expectedResult["id"] = resultJSON["id"]
    expectedResult[object_store_abstraction.RepositoryObjBaseClass.getMetadataElementKey()] = {
      "creationDateTime": testTime.isoformat(),
      "lastUpdateDateTime": testTime.isoformat(),
      "objectKey": resultJSON["id"],
      "objectVersion": "1"
    }
    python_Testing_Utilities.assertObjectsEqual(
      unittestTestCaseClass=self,
      first=resultJSON,
      second=expectedResult,
      msg="JSON of created Ticket Type is not the same",
      ignoredRootKeys=[]
    )

    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON, expectedResult, [], msg='JSON of created Ticket Type is not the same')

  def test_createWithMetadataShouldFail(self):
    obj = copy.deepcopy(ticketManagerTestCommon.validTicketTypeDict)
    obj[object_store_abstraction.RepositoryObjBaseClass.getMetadataElementKey()] = {}
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants/' + constants.masterTenantName + '/tickettypes',
      headers={ constants.jwtHeaderName: self.getNormalJWTToken()},
      data=json.dumps(obj),
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400)


