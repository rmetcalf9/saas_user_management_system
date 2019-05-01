from datetime import datetime, timedelta
import pytz
from TestHelperSuperClass import testHelperAPIClient, env, tenantWithNoAuthProviders, sampleInternalAuthProv001_CREATE, internalUSerSufix
from appObj import appObj
from constants import masterTenantName, jwtHeaderName, objectVersionHeaderName, DefaultHasAccountRole, masterTenantDefaultSystemAdminRole, uniqueKeyCombinator
from test_adminAPI import test_api as parent_test_api
from test_adminAPI_users import defaultUserData
import json
import copy

#Test person functoins of the admin API


defaultPersonData = {
  'guid': "SOMEVALUE",
  'ObjectVersion': "1",
  "associatedUsers": [defaultUserData],
  "personAuths": [{
    "AuthProviderGUID": "574a7b51-110d-4fcd-b4a4-868884922109", 
    "AuthProviderType": "internal", 
    "AuthUserKey": "AdminTestSet" + internalUSerSufix + uniqueKeyCombinator +"internal",
    "known_as": "AdminTestSet",
    "tenantName": masterTenantName
  }]
}


class test_adminAPIPersons(parent_test_api):
  def test_getDefaultListFromMasterTenant(self):
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/persons', headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    
    resultJSON = json.loads(result.get_data(as_text=True))
    self.assertEqual(resultJSON['pagination']['total'],1)
    
    masterTenantDictTenantDict = self.getTenantDICT(masterTenantName)
    
    defaultPersonDataAltered = copy.deepcopy(defaultPersonData)
    defaultPersonDataAltered["personAuths"][0]["AuthProviderGUID"] = masterTenantDictTenantDict["AuthProviders"][0]["guid"]
    UnknownVals = ["creationDateTime", "lastUpdateDateTime", "guid", "associatedUsers"]
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON['result'][0],defaultPersonDataAltered, UnknownVals, msg="Person data mismatch")
    self.assertEqual(len(resultJSON['result'][0]["associatedUsers"]),1)
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON['result'][0]["associatedUsers"][0],defaultPersonData["associatedUsers"][0], ["creationDateTime", "lastUpdateDateTime"], msg="Person data mismatch")

    self.assertEqual(len(resultJSON['result']),1,msg="Wrong number of person results returned")
    for a in UnknownVals:
      self.assertTrue(a in resultJSON['result'][0], msg=a + " is not in resultJSON['result'][0]") 

  def test_createNewPersonUsingAdminAPI(self):
    self.createPersonAndReturnDICT()
    
  def test_createNewPersonSupplyingGUIDFails(self):
    newPersonDICT = {
      "guid": "123"
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/persons', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newPersonDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg="Create person should have failed - " + result.get_data(as_text=True))

    
  def test_getPerson(self):
    personDICT = self.createPersonAndReturnDICT()
    
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/persons/' + personDICT['guid'], headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)

    resultJSON = json.loads(result.get_data(as_text=True))

    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON,personDICT, [], msg="Returned Person data wrong")

  #updateperson
  def test_updatePerson(self):
    createPersonTime = datetime.now(pytz.timezone("UTC"))
    updatePersonTime = createPersonTime + timedelta(seconds=int(12))
    
    appObj.setTestingDateTime(createPersonTime)
    personDICT = self.createPersonAndReturnDICT()
    
    updPersonDict = copy.deepcopy(personDICT)
    
    appObj.setTestingDateTime(updatePersonTime)
    putResult = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/persons/' + personDICT['guid'], 
      data=json.dumps(updPersonDict), 
      content_type='application/json', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}
    )
    self.assertEqual(putResult.status_code, 200, msg="Update Person failed - " + putResult.get_data(as_text=True))
    putResultJSON = json.loads(putResult.get_data(as_text=True))

    expectedResult = copy.deepcopy(updPersonDict)
    expectedResult['ObjectVersion'] = "2"
    expectedResult['creationDateTime'] = createPersonTime.isoformat()
    expectedResult['lastUpdateDateTime'] = updatePersonTime.isoformat()
    
    self.assertJSONStringsEqualWithIgnoredKeys(putResultJSON,expectedResult, [], msg="Returned Person data wrong")
    
  def test_updatePersonDosentExistThrowsError(self):
    personDICT = self.createPersonAndReturnDICT()
    putResult = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/persons/' + 'bad_person_guid', 
      data=json.dumps(personDICT), 
      content_type='application/json', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}
    )
    self.assertEqual(putResult.status_code, 400, msg="Update Person which dosen't exist did not fail - " + putResult.get_data(as_text=True))
  
  def test_updatePersonWithWrongObjectVersion(self):
    personDICT = self.createPersonAndReturnDICT()
    personDICT['ObjectVersion'] = "0"
    putResult = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/persons/' + personDICT['guid'], 
      data=json.dumps(personDICT), 
      content_type='application/json', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}
    )
    self.assertEqual(putResult.status_code, 409, msg="Update Person with wrong object version did not fail - " + putResult.get_data(as_text=True))
 
  def test_deletePerson(self):
    personDICT = self.createPersonAndReturnDICT()
    
    deleteResult = self.testClient.delete(
      self.adminAPIPrefix + '/' + masterTenantName + '/persons/' + personDICT['guid'], 
      headers={ jwtHeaderName: self.getNormalJWTToken(), objectVersionHeaderName: personDICT['ObjectVersion']}
    )
    self.assertEqual(deleteResult.status_code, 200, msg="Delete person failed - " + deleteResult.get_data(as_text=True)) 
    deleteResultJSON = json.loads(deleteResult.get_data(as_text=True))
    self.assertJSONStringsEqualWithIgnoredKeys(deleteResultJSON,personDICT, [], msg="Delete Returned bad Person data")
    
    #Try and retrieve the deleted person
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/persons/' + personDICT['guid'], headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 404, msg="Person still in system")

  def test_deleteWrongObjectVersionFails(self):
    personDICT = self.createPersonAndReturnDICT()
    personDICT['ObjectVersion'] = "0"
    
    deleteResult = self.testClient.delete(
      self.adminAPIPrefix + '/' + masterTenantName + '/persons/' + personDICT['guid'], 
      headers={ jwtHeaderName: self.getNormalJWTToken(), objectVersionHeaderName: personDICT['ObjectVersion']}
    )
    self.assertEqual(deleteResult.status_code, 409, msg="Delete person did not fail - " + deleteResult.get_data(as_text=True)) 

  def test_deletNonExistingPersonFails(self):
    deleteResult = self.testClient.delete(
      self.adminAPIPrefix + '/' + masterTenantName + '/persons/' + 'bad_guid', 
      headers={ jwtHeaderName: self.getNormalJWTToken(), objectVersionHeaderName: "1"}
    )
    self.assertEqual(deleteResult.status_code, 400, msg="Delete person did not fail - " + deleteResult.get_data(as_text=True)) 

  def test_deleteLoggedInUserFails(self):
    #The main personGUID is set to appObj.defaultUserGUID in testing mode
    deleteResult = self.testClient.delete(
      self.adminAPIPrefix + '/' + masterTenantName + '/persons/' + appObj.testingDefaultPersonGUID, 
      headers={ jwtHeaderName: self.getNormalJWTToken(), objectVersionHeaderName: "1"}
    )
    self.assertEqual(deleteResult.status_code, 400, msg="Delete logged in user did not fail - " + deleteResult.get_data(as_text=True)) 
  
    
  #TODO Test delete person with an auth deletes the auth