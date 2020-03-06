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
from ticketManager__Common_API import ticketManagerAPICommonUtilsClass

class helper(ticketManagerAPICommonUtilsClass):
  def updateTicketType(self, tenantTypeID, tenantTypesTenant, newDict, checkAndParseResponse=True):
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants/' + tenantTypesTenant + '/tickettypes/' + tenantTypeID,
      headers={constants.jwtHeaderName: self.getNormalJWTToken()},
      data=json.dumps(newDict),
      content_type='application/json'
    )
    if not checkAndParseResponse:
      return result
    self.assertEqual(result.status_code, 202, msg="Err: " + result.get_data(as_text=True))
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

  def deleteTicketType(self, tenantTypesTenant, ticketTypeID, objectVersionNumber, checkAndParseResponse=True):
    result2 = self.testClient.delete(
      self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants/' + tenantTypesTenant + '/tickettypes/' + ticketTypeID + "?objectversion=" + objectVersionNumber,
      headers={ constants.jwtHeaderName: self.getNormalJWTToken()},
      data=None,
      content_type='application/json'
    )
    if not checkAndParseResponse:
      return result2
    self.assertEqual(result2.status_code, 202)
    return json.loads(result2.get_data(as_text=True))

  def setupTestTicketsInTwoTenants(self):
    okTicketResultJSON = []
    okTicketResultJSONIDMap = {}
    okTicketResultJSON.append(self.createTicketType(constants.masterTenantName, overrideName="TestTicketType001"))
    okTicketResultJSONIDMap[okTicketResultJSON[len(okTicketResultJSON)-1]["id"]] = len(okTicketResultJSON)-1
    okTicketResultJSON.append(self.createTicketType(constants.masterTenantName, overrideName="TestTicketType002"))
    okTicketResultJSONIDMap[okTicketResultJSON[len(okTicketResultJSON)-1]["id"]] = len(okTicketResultJSON)-1
    okTicketResultJSON.append(self.createTicketType(constants.masterTenantName, overrideName="TestTicketType003"))
    okTicketResultJSONIDMap[okTicketResultJSON[len(okTicketResultJSON)-1]["id"]] = len(okTicketResultJSON)-1

    #Create some on another tenant
    tenantJSON = self.createTenantForTesting(TestHelperSuperClass.tenantWithNoAuthProviders)
    noiseTicketResultJSON = []
    noiseTicketResultJSONMap = {}
    noiseTicketResultJSON.append(self.createTicketType(TestHelperSuperClass.tenantWithNoAuthProviders["Name"], overrideName="TestTicketType004"))
    noiseTicketResultJSONMap[noiseTicketResultJSON[len(noiseTicketResultJSON)-1]["id"]] = len(noiseTicketResultJSON)-1
    noiseTicketResultJSON.append(self.createTicketType(TestHelperSuperClass.tenantWithNoAuthProviders["Name"], overrideName="TestTicketType005"))
    noiseTicketResultJSONMap[noiseTicketResultJSON[len(noiseTicketResultJSON)-1]["id"]] = len(noiseTicketResultJSON)-1
    noiseTicketResultJSON.append(self.createTicketType(TestHelperSuperClass.tenantWithNoAuthProviders["Name"], overrideName="TestTicketType006"))
    noiseTicketResultJSONMap[noiseTicketResultJSON[len(noiseTicketResultJSON)-1]["id"]] = len(noiseTicketResultJSON)-1

    return {
      "okTicketResultJSON": okTicketResultJSON,
      "okTicketResultJSONIDMap": okTicketResultJSONIDMap,
      "tenantJSON": tenantJSON,
      "noiseTicketResultJSON": noiseTicketResultJSON,
      "noiseTicketResultJSONMap": noiseTicketResultJSONMap
    }

#@TestHelperSuperClass.wipd
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

  def test_createWithHasAccountRoleFail(self):
    obj = copy.deepcopy(ticketManagerTestCommon.validTicketTypeDict)
    obj["roles"].append(constants.DefaultHasAccountRole)
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants/' + constants.masterTenantName + '/tickettypes',
      headers={ constants.jwtHeaderName: self.getNormalJWTToken()},
      data=json.dumps(obj),
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400)

  def test_createWithNoRolesFail(self):
    obj = copy.deepcopy(ticketManagerTestCommon.validTicketTypeDict)
    obj["roles"] = []
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
    setupData = self.setupTestTicketsInTwoTenants()

    queryResultJSON = self.getTicketTypes(constants.masterTenantName, queryString=None, checkAndParseResponse=True)

    self.assertEqual(queryResultJSON["pagination"]["total"], 3)
    foundIDs = []
    for x in queryResultJSON["result"]:
      if x["id"] not in setupData["okTicketResultJSONIDMap"]:
        self.assertTrue(False, msg="Found unknown result")
      if x["id"] in foundIDs:
        self.assertTrue(False, msg="Found same TicketType twice")
      foundIDs.append(x["id"])
    self.assertEqual(len(foundIDs), 3)

  def test_QueryBackSingleTicketTypeUsingFilter(self):
    setupData = self.setupTestTicketsInTwoTenants()

    queryResultJSON = self.getTicketTypes(constants.masterTenantName, queryString=setupData["okTicketResultJSON"][1]["ticketTypeName"], checkAndParseResponse=True)

    self.assertEqual(queryResultJSON["pagination"]["total"], 1)
    self.assertEqual(queryResultJSON["result"][0]["id"], setupData["okTicketResultJSON"][1]["id"])

  def test_DeleteTicketType(self):
    setupData = self.setupTestTicketsInTwoTenants()

    queryResultJSON = self.getTicketTypes(constants.masterTenantName, queryString=None, checkAndParseResponse=True)
    self.assertEqual(queryResultJSON["pagination"]["total"], 3)

    deleteResultJSON = self.deleteTicketType(
      tenantTypesTenant=constants.masterTenantName,
      ticketTypeID=setupData["okTicketResultJSON"][1]["id"],
      objectVersionNumber=setupData["okTicketResultJSON"][1][object_store_abstraction.RepositoryObjBaseClass.getMetadataElementKey()]["objectVersion"]
    )
    queryResultJSON2 = self.getTicketTypes(constants.masterTenantName, queryString=None, checkAndParseResponse=True)
    for x in queryResultJSON2["result"]:
      self.assertNotEqual(x["id"], setupData["okTicketResultJSON"][1]["id"], msg="Found deleted ticket in result")
    self.assertEqual(queryResultJSON2["pagination"]["total"], 2)

    #TODO When tickets are imlemented this should also delete all the tickets

  def test_DeleteTicketTypeWrongObjectVersionNumFails(self):
    setupData = self.setupTestTicketsInTwoTenants()

    deleteResultRAW = self.deleteTicketType(
      tenantTypesTenant=constants.masterTenantName,
      ticketTypeID=setupData["okTicketResultJSON"][1]["id"],
      objectVersionNumber="999",
      checkAndParseResponse=False
    )
    self.assertEqual(deleteResultRAW.status_code, 409, msg="Should have failed to delete " + deleteResultRAW.get_data(as_text=True))

  def test_DeleteTicketTypeWrongTenantFails(self):
    setupData = self.setupTestTicketsInTwoTenants()

    deleteResultRAW = self.deleteTicketType(
      tenantTypesTenant=constants.masterTenantName,
      ticketTypeID=setupData["noiseTicketResultJSON"][1]["id"],
      objectVersionNumber=setupData["noiseTicketResultJSON"][1][object_store_abstraction.RepositoryObjBaseClass.getMetadataElementKey()]["objectVersion"],
      checkAndParseResponse=False
    )
    self.assertEqual(deleteResultRAW.status_code, 404, msg="Should have failed to delete " + deleteResultRAW.get_data(as_text=True))

  def test_DeleteNonExistantticketTypeFails(self):
    setupData = self.setupTestTicketsInTwoTenants()

    deleteResultRAW = self.deleteTicketType(
      tenantTypesTenant=constants.masterTenantName,
      ticketTypeID="EDFVF4",
      objectVersionNumber=setupData["noiseTicketResultJSON"][1][object_store_abstraction.RepositoryObjBaseClass.getMetadataElementKey()]["objectVersion"],
      checkAndParseResponse=False
    )
    self.assertEqual(deleteResultRAW.status_code, 404, msg="Should have failed to delete " + deleteResultRAW.get_data(as_text=True))

  def test_updateTicketType(self):
    testTime1 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime1)
    setupData = self.setupTestTicketsInTwoTenants()

    testTime2 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime2)
    changed = copy.deepcopy(setupData["okTicketResultJSON"][1])
    changed["ticketTypeName"] = "okTicketResultJSONUPDATED"
    resultJSON = self.updateTicketType(tenantTypeID=setupData["okTicketResultJSON"][1]["id"], tenantTypesTenant=constants.masterTenantName, newDict=changed)

    expectedResult = copy.deepcopy(changed)
    expectedResult["id"] = resultJSON["id"]
    expectedResult[object_store_abstraction.RepositoryObjBaseClass.getMetadataElementKey()] = {
      "creationDateTime": testTime1.isoformat(),
      "lastUpdateDateTime": testTime2.isoformat(),
      "objectKey": resultJSON["id"],
      "objectVersion": "2" #We expect an updated object
    }
    python_Testing_Utilities.assertObjectsEqual(
      unittestTestCaseClass=self,
      first=resultJSON,
      second=expectedResult,
      msg="JSON of created Ticket Type is not the same",
      ignoredRootKeys=[]
    )

    #Not get the ticket type we just created and make sure it matches
    resultJSON2 = self.getTicketType(constants.masterTenantName, setupData["okTicketResultJSON"][1]["id"])
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON2, expectedResult, [], msg='Get retrevial mismatch')

  def test_updateInvalidObjectID(self):
    testTime1 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime1)
    setupData = self.setupTestTicketsInTwoTenants()

    testTime2 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime2)
    changed = copy.deepcopy(setupData["okTicketResultJSON"][1])
    changed["ticketTypeName"] = "okTicketResultJSONUPDATED"
    changed["id"] = "WrongIDVal"
    resultRAW = self.updateTicketType(
      tenantTypeID=changed["id"],
      tenantTypesTenant=constants.masterTenantName,
      newDict=changed,
      checkAndParseResponse=False
    )
    self.assertEqual(resultRAW.status_code, 404, msg="Err: should have failed " + resultRAW.get_data(as_text=True))


  def test_updateIDMustMatchURLID_URLWRONG(self):
    testTime1 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime1)
    setupData = self.setupTestTicketsInTwoTenants()

    testTime2 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime2)
    changed = copy.deepcopy(setupData["okTicketResultJSON"][1])
    changed["ticketTypeName"] = "okTicketResultJSONUPDATED"
    resultRAW = self.updateTicketType(
      tenantTypeID="someOtherID",
      tenantTypesTenant=constants.masterTenantName,
      newDict=changed,
      checkAndParseResponse=False
    )
    self.assertEqual(resultRAW.status_code, 400, msg="Err: should have failed " + resultRAW.get_data(as_text=True))

  def test_updateIDMustMatchURLID_IDWRONG(self):
    testTime1 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime1)
    setupData = self.setupTestTicketsInTwoTenants()

    testTime2 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime2)
    changed = copy.deepcopy(setupData["okTicketResultJSON"][1])
    changed["ticketTypeName"] = "okTicketResultJSONUPDATED"
    changed["id"] = "WrongIDVal"
    resultRAW = self.updateTicketType(
      tenantTypeID=setupData["okTicketResultJSON"][1]["id"],
      tenantTypesTenant=constants.masterTenantName,
      newDict=changed,
      checkAndParseResponse=False
    )
    self.assertEqual(resultRAW.status_code, 400, msg="Err: should have failed " + resultRAW.get_data(as_text=True))


  def test_updateURLTenantMismachFails(self):
    testTime1 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime1)
    setupData = self.setupTestTicketsInTwoTenants()
    testTime2 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime2)
    changed = copy.deepcopy(setupData["okTicketResultJSON"][1])
    changed["ticketTypeName"] = "okTicketResultJSONUPDATED"
    changed["tenantName"] = setupData["tenantJSON"]["Name"]
    resultRAW = self.updateTicketType(
      tenantTypeID=setupData["okTicketResultJSON"][1]["id"],
      tenantTypesTenant=constants.masterTenantName,
      newDict=changed,
      checkAndParseResponse=False
    )
    self.assertEqual(resultRAW.status_code, 400, msg="Err: should have failed " + resultRAW.get_data(as_text=True))

  def test_updateChangingTenantFails(self):
    testTime1 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime1)
    setupData = self.setupTestTicketsInTwoTenants()
    testTime2 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime2)
    changed = copy.deepcopy(setupData["okTicketResultJSON"][1])
    changed["ticketTypeName"] = "okTicketResultJSONUPDATED"
    changed["tenantName"] = setupData["tenantJSON"]["Name"]
    resultRAW = self.updateTicketType(
      tenantTypeID=setupData["okTicketResultJSON"][1]["id"],
      tenantTypesTenant=setupData["tenantJSON"]["Name"],
      newDict=changed,
      checkAndParseResponse=False
    )
    #Tried to change the tenant name on a ticket - result in it not being found
    self.assertEqual(resultRAW.status_code, 404, msg="Err: should have failed " + resultRAW.get_data(as_text=True))

  def test_updateAddingUserAccountRoleFails(self):
    testTime1 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime1)
    setupData = self.setupTestTicketsInTwoTenants()

    testTime2 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime2)
    changed = copy.deepcopy(setupData["okTicketResultJSON"][1])
    changed["ticketTypeName"] = "okTicketResultJSONUPDATED"
    changed["roles"].append(constants.DefaultHasAccountRole)
    resultRAW = self.updateTicketType(
      tenantTypeID=setupData["okTicketResultJSON"][1]["id"],
      tenantTypesTenant=constants.masterTenantName,
      newDict=changed,
      checkAndParseResponse=False
    )
    self.assertEqual(resultRAW.status_code, 400, msg="Err: should have failed " + resultRAW.get_data(as_text=True))

  def test_updateWrongObjectversionFails(self):
    testTime1 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime1)
    setupData = self.setupTestTicketsInTwoTenants()

    testTime2 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime2)
    changed = copy.deepcopy(setupData["okTicketResultJSON"][1])
    changed["ticketTypeName"] = "okTicketResultJSONUPDATED"
    changed[object_store_abstraction.RepositoryObjBaseClass.getMetadataElementKey()]["objectVersion"] = 999
    resultRAW = self.updateTicketType(
      tenantTypeID=setupData["okTicketResultJSON"][1]["id"],
      tenantTypesTenant=constants.masterTenantName,
      newDict=changed,
      checkAndParseResponse=False
    )
    self.assertEqual(resultRAW.status_code, 400, msg="Err: should have failed " + resultRAW.get_data(as_text=True))

  def tesT_updateMissingObjectversionElementFails(self):
    testTime1 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime1)
    setupData = self.setupTestTicketsInTwoTenants()

    testTime2 = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testTime2)
    changed = copy.deepcopy(setupData["okTicketResultJSON"][1])
    changed["ticketTypeName"] = "okTicketResultJSONUPDATED"
    del changed[object_store_abstraction.RepositoryObjBaseClass.getMetadataElementKey()]
    resultRAW = self.updateTicketType(
      tenantTypeID=setupData["okTicketResultJSON"][1]["id"],
      tenantTypesTenant=constants.masterTenantName,
      newDict=changed,
      checkAndParseResponse=False
    )
    self.assertEqual(resultRAW.status_code, 400, msg="Err: should have failed " + resultRAW.get_data(as_text=True))
