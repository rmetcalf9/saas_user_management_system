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

  def getTicketType(self, tenantTypesTenant, ticketTypeID, checkAndParseResponse=True):
    result2 = self.testClient.get(
      self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants/' + tenantTypesTenant + '/tickettypes/' + ticketTypeID,
      headers={ constants.jwtHeaderName: self.getNormalJWTToken()},
      data=None,
      content_type='application/json'
    )
    if not checkAndParseResponse:
      return result2
    self.assertEqual(result2.status_code, 200)
    return json.loads(result2.get_data(as_text=True))

  def getTicketTypes(self, tenantTypesTenant, queryString=None, checkAndParseResponse=True):
    postfix = ""
    if queryString is not None:
      postfix= "?query=" + queryString

    result2 = self.testClient.get(
      self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants/' + tenantTypesTenant + '/tickettypes' + postfix,
      headers={constants.jwtHeaderName: self.getNormalJWTToken()},
      data=None,
      content_type='application/json'
    )
    if not checkAndParseResponse:
      return result2
    self.assertEqual(result2.status_code, 200)
    return json.loads(result2.get_data(as_text=True))


@TestHelperSuperClass.wipd
class ticketManager_helpers(helper):
  def test_createValidTicketType(self):
    testTime = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime)
    resultJSON = self.createTicketType(constants.masterTenantName)

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

    #Not get the ticket type we just created and make sure it matches
    resultJSON2 = self.getTicketType(constants.masterTenantName, resultJSON["id"])
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON2, expectedResult, [], msg='Get retrevial failed')

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

  def test_canOnlyRetrieveTicketTypeForURLTenant(self):
    tenantJSON = self.createTenantForTesting(TestHelperSuperClass.tenantWithNoAuthProviders)
    resultJSON = self.createTicketType(constants.masterTenantName)
    resultRAW = self.getTicketType(TestHelperSuperClass.tenantWithNoAuthProviders["Name"], resultJSON["id"], checkAndParseResponse=False)
    self.assertEqual(resultRAW.status_code, 404)

  def test_RetrieveThreeTicketTypes(self):
    resultJSONIDS = {}
    resultJSON = self.createTicketType(constants.masterTenantName, overrideName="TestTicketType001")
    resultJSONIDS[resultJSON["id"]] = True
    resultJSON = self.createTicketType(constants.masterTenantName, overrideName="TestTicketType002")
    resultJSONIDS[resultJSON["id"]] = True
    resultJSON = self.createTicketType(constants.masterTenantName, overrideName="TestTicketType003")
    resultJSONIDS[resultJSON["id"]] = True

    queryResultJSON = self.getTicketTypes(constants.masterTenantName, queryString=None, checkAndParseResponse=True)

    self.assertEqual(queryResultJSON["pagination"]["total"], 3)
    foundIDs = []
    for x in queryResultJSON["result"]:
      if x["id"] not in resultJSONIDS:
        self.assertTrue(False, msg="Found unknown result")
      if x["id"] in foundIDs:
        self.assertTrue(False, msg="Found same TicketType twice")
      foundIDs.append(x["id"])
    self.assertEqual(len(foundIDs), 3)

  def test_TicketTypeListRetervalOnlyCountsOneTenant(self):
    resultJSONIDS = {}
    resultJSON = self.createTicketType(constants.masterTenantName, overrideName="TestTicketType001")
    resultJSONIDS[resultJSON["id"]] = True
    resultJSON = self.createTicketType(constants.masterTenantName, overrideName="TestTicketType002")
    resultJSONIDS[resultJSON["id"]] = True
    resultJSON = self.createTicketType(constants.masterTenantName, overrideName="TestTicketType003")
    resultJSONIDS[resultJSON["id"]] = True

    #Create some on another tenant
    tenantJSON = self.createTenantForTesting(TestHelperSuperClass.tenantWithNoAuthProviders)
    resultJSONNoise = self.createTicketType(TestHelperSuperClass.tenantWithNoAuthProviders["Name"], overrideName="TestTicketType004")
    resultJSONNoise = self.createTicketType(TestHelperSuperClass.tenantWithNoAuthProviders["Name"], overrideName="TestTicketType005")
    resultJSONNoise = self.createTicketType(TestHelperSuperClass.tenantWithNoAuthProviders["Name"], overrideName="TestTicketType006")

    queryResultJSON = self.getTicketTypes(constants.masterTenantName, queryString=None, checkAndParseResponse=True)

    self.assertEqual(queryResultJSON["pagination"]["total"], 3)
    foundIDs = []
    for x in queryResultJSON["result"]:
      if x["id"] not in resultJSONIDS:
        self.assertTrue(False, msg="Found unknown result")
      if x["id"] in foundIDs:
        self.assertTrue(False, msg="Found same TicketType twice")
      foundIDs.append(x["id"])
    self.assertEqual(len(foundIDs), 3)

  def test_QueryBackSingleTicketTypeUsingFilter(self):
    resultJSON1 = self.createTicketType(constants.masterTenantName, overrideName="TestTicketType001")
    resultJSON2 = self.createTicketType(constants.masterTenantName, overrideName="TestTicketType002")
    resultJSON3 = self.createTicketType(constants.masterTenantName, overrideName="TestTicketType003")

    #Create some on another tenant
    tenantJSON = self.createTenantForTesting(TestHelperSuperClass.tenantWithNoAuthProviders)
    resultJSONNoise = self.createTicketType(TestHelperSuperClass.tenantWithNoAuthProviders["Name"], overrideName="TestTicketType004")
    resultJSONNoise = self.createTicketType(TestHelperSuperClass.tenantWithNoAuthProviders["Name"], overrideName="TestTicketType005")
    resultJSONNoise = self.createTicketType(TestHelperSuperClass.tenantWithNoAuthProviders["Name"], overrideName="TestTicketType006")

    queryResultJSON = self.getTicketTypes(constants.masterTenantName, queryString=resultJSON2["ticketTypeName"], checkAndParseResponse=True)

    self.assertEqual(queryResultJSON["pagination"]["total"], 1)
    self.assertEqual(queryResultJSON["result"][0]["id"], resultJSON2["id"])


