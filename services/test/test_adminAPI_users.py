from datetime import datetime, timedelta
import pytz
from TestHelperSuperClass import testHelperAPIClient, env, tenantWithNoAuthProviders, sampleInternalAuthProv001_CREATE, internalUSerSufix
from appObj import appObj
from constants import masterTenantName, jwtHeaderName, objectVersionHeaderName, DefaultHasAccountRole, masterTenantDefaultSystemAdminRole
from test_adminAPI import test_api as parent_test_api
import json
import copy

#Test user functoins of the admin API

defaultUserData = {
  'UserID': appObj.defaultUserGUID,
  'known_as': env['APIAPP_DEFAULTHOMEADMINUSERNAME'],
  'TenantRoles': [{
    'TenantName': masterTenantName,
    'ThisTenantRoles': [masterTenantDefaultSystemAdminRole, DefaultHasAccountRole]
  }],
  'other_data': {
    "createdBy": "init/CreateMasterTenant"
  },
  "associatedPersonGUIDs": ["FORCED-CONSTANT-TESTING-PERSON-GUID"],
  'ObjectVersion': "3"
}

class test_adminAPIUsers(parent_test_api):
  def test_getDefaultListFromMasterTenant(self):
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/users', headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    
    resultJSON = json.loads(result.get_data(as_text=True))
    self.assertEqual(resultJSON['pagination']['total'],1)
    
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON['result'][0],defaultUserData, ["associatedPersonGUIDs", "TenantRoles", "creationDateTime", "lastUpdateDateTime"], msg="User data mismatch")
    
    self.assertEqual(len(resultJSON['result'][0]["TenantRoles"]),1,msg="Didn't return single tenant")

    expectedTenantRolesResult = [{
      "TenantName": masterTenantName,
      "ThisTenantRoles": [masterTenantDefaultSystemAdminRole, DefaultHasAccountRole]
    }]
    
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON['result'][0]["TenantRoles"],expectedTenantRolesResult, ["TenantRoles"], msg="Tenant Roles returned data wrong")
    
  def test_getUserListThreeTenantsAndMutipleUsers(self):
    testDateTime = datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testDateTime)
    tenantDict = self.setupTenantForTesting(tenantWithNoAuthProviders, True, True)

    createdAuthProvGUID = tenantDict['AuthProviders'][0]['guid']
    createdAuthSalt = tenantDict['AuthProviders'][0]['saltForPasswordHashing']
    userName = "testSetUserName"
    
    registerJSON = {
      "authProviderGUID": createdAuthProvGUID,
      "credentialJSON": { 
        "username": userName, 
        "password": self.getDefaultHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(createdAuthSalt)
       }
    }
    
    registerResult = self.testClient.put(
      self.loginAPIPrefix + '/' + tenantWithNoAuthProviders['Name'] + '/register', 
      data=json.dumps(registerJSON), 
      content_type='application/json'
    )
    self.assertEqual(registerResult.status_code, 201, msg="Registration failed")


    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/users', headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    
    resultJSON = json.loads(result.get_data(as_text=True))
    self.assertEqual(resultJSON['pagination']['total'], 2, msg="Wrong number of users returned")
    
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON['result'][0],defaultUserData, ["TenantRoles", "creationDateTime", "lastUpdateDateTime", 'associatedPersonGUIDs'], msg="User data mismatch")
    self.assertEqual(len(resultJSON['result'][0]["TenantRoles"]),1,msg="Didn't return single tenant")
    expectedTenantRolesResult = [{
      "TenantName": masterTenantName,
      "ThisTenantRoles": [masterTenantDefaultSystemAdminRole, DefaultHasAccountRole]
    }]
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON['result'][0]["TenantRoles"],expectedTenantRolesResult, ["TenantRoles"], msg="Tenant Roles returned data wrong")
   
    expectedResult = {
      'UserID': userName + internalUSerSufix,
      'known_as': userName,
      'other_data': {
        "createdBy": "loginapi/register"
      },
      'ObjectVersion': "2"
    }
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON['result'][1],expectedResult, ["TenantRoles", "creationDateTime", "lastUpdateDateTime", 'associatedPersonGUIDs'], msg="User data mismatch")
    self.assertEqual(len(resultJSON['result'][1]["TenantRoles"]),1,msg="Didn't return single tenant")
    expectedTenantRolesResult = [{
      "TenantName": tenantDict["Name"],
      "ThisTenantRoles": [DefaultHasAccountRole]
    }]
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON['result'][1]["TenantRoles"],expectedTenantRolesResult, ["TenantRoles"], msg="Tenant Roles returned data wrong")
   
  def test_getSingleUser(self):
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/users/' + appObj.defaultUserGUID, headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)

    resultJSON = json.loads(result.get_data(as_text=True))

    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON,defaultUserData, ["TenantRoles", "creationDateTime", "lastUpdateDateTime", 'associatedPersonGUIDs'], msg="Returned user data")
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON["TenantRoles"],defaultUserData["TenantRoles"], [], msg="Returned user data")
    self.assertEqual(len(resultJSON["associatedPersonGUIDs"]),1)
    
  def test_updateUserData(self):
    testDateTime = datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testDateTime)
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/users/' + appObj.defaultUserGUID, headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    origUserDICT = json.loads(result.get_data(as_text=True))
    #ObjectVersion copied in from result

    newUserDICT = copy.deepcopy(origUserDICT)
    newUserDICT['known_as'] = 'ChangedValue'
    newUserDICT['other_data'] = {
      'a': "A",
      'b': "B"
    }
    newUserDICT["creationDateTime"] = testDateTime.isoformat() #Main user is created before the testing date is set
    newUserDICT["lastUpdateDateTime"] = testDateTime.isoformat()
    
    print(testDateTime.isoformat())

    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/users/' + appObj.defaultUserGUID, 
      data=json.dumps(newUserDICT), 
      content_type='application/json',
      headers={ jwtHeaderName: self.getNormalJWTToken()}
    )
    self.assertEqual(result.status_code, 200)
    newUserDICT['ObjectVersion'] = str(int(newUserDICT['ObjectVersion']) + 1)
    
    resultJSON = json.loads(result.get_data(as_text=True))
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON,newUserDICT, ["TenantRoles", "creationDateTime"], msg="Returned user data")
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON["TenantRoles"],newUserDICT["TenantRoles"], [], msg="Returned user data")


    result2 = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/users/' + appObj.defaultUserGUID, headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result2.status_code, 200)
    result2JSON = json.loads(result2.get_data(as_text=True))
    self.assertJSONStringsEqualWithIgnoredKeys(result2JSON,newUserDICT, ["TenantRoles", "creationDateTime"], msg="Returned user data")
    self.assertJSONStringsEqualWithIgnoredKeys(result2JSON["TenantRoles"],newUserDICT["TenantRoles"], [], msg="Returned user data")

    
    
  def test_updateUserDataTryAndChangeUserID(self):
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/users/' + appObj.defaultUserGUID, headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    origUserDICT = json.loads(result.get_data(as_text=True))
    #ObjectVersion copied in from result

    newUserDICT = copy.deepcopy(origUserDICT)
    newUserDICT['UserID'] = 'ChangedValue'
    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/users/' + appObj.defaultUserGUID, 
      data=json.dumps(newUserDICT), 
      content_type='application/json',
      headers={ jwtHeaderName: self.getNormalJWTToken()}
    )
    self.assertEqual(result.status_code, 400, msg=result.get_data(as_text=True))
  
  #delete user test
  def test_deleteUser(self):
    tenantDict = self.setupTenantForTesting(tenantWithNoAuthProviders, True, True)
    createdAuthProvGUID = tenantDict['AuthProviders'][0]['guid']
    createdAuthSalt = tenantDict['AuthProviders'][0]['saltForPasswordHashing']

    registerJSON = {
      "authProviderGUID": createdAuthProvGUID,
      "credentialJSON": { 
        "username": "TTT", 
        "password": self.getDefaultHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(createdAuthSalt)
       }
    }
    registerResult = self.testClient.put(
      self.loginAPIPrefix + '/' + tenantDict['Name'] + '/register', 
      data=json.dumps(registerJSON), 
      content_type='application/json'
    )
    self.assertEqual(registerResult.status_code, 201, msg="Registration failed - " + registerResult.get_data(as_text=True))
    resultJSON = json.loads(registerResult.get_data(as_text=True))
    createdUserID = resultJSON["UserID"]
    
    result = self.testClient.delete(
      self.adminAPIPrefix + '/' + masterTenantName + '/users/' + createdUserID, 
      headers={ jwtHeaderName: self.getNormalJWTToken(), objectVersionHeaderName: tenantDict['ObjectVersion']}
    )
    self.assertEqual(result.status_code, 200, msg="Delete user failed - " + result.get_data(as_text=True)) 

    #Try and retrieve the deleted user
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/users/' + createdUserID, headers={ jwtHeaderName: self.getNormalJWTToken()})
    #print(result.get_data(as_text=True))
    self.assertEqual(result.status_code, 404, msg="User still in system")

  
  #make sure we can't delete currently logged in user
  def test_tryToDeleteCurrentlyLoggedInUser(self):
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/users/' + appObj.defaultUserGUID, headers={ jwtHeaderName: self.getNormalJWTToken()})
    resultJSON = json.loads(result.get_data(as_text=True))
    masterUserID = resultJSON["UserID"]
    objectVersion = resultJSON["ObjectVersion"]

    result = self.testClient.delete(
      self.adminAPIPrefix + '/' + masterTenantName + '/users/' + appObj.defaultUserGUID, 
      headers={ jwtHeaderName: self.getNormalJWTToken(), objectVersionHeaderName: objectVersion}
    )
    self.assertEqual(result.status_code, 400, msg="Delete user did not fail") 
  
  #delete non existant user fails
  def test_tryToDeleteNonExistantUser(self):
    result = self.testClient.delete(
      self.adminAPIPrefix + '/' + masterTenantName + '/users/' + "nonxsistantUserID", 
      headers={ jwtHeaderName: self.getNormalJWTToken(), objectVersionHeaderName: "1"}
    )
    self.assertEqual(result.status_code, 400, msg="non existant user deletion did not fail") 


  def test_createNewUserUsingAdminAPI(self):
    newUserDICT = {
      "UserID": "testUserID@TestUser",
      "known_as": "testUserID",
      "mainTenant": masterTenantName
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/users', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newUserDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 201, msg="Create user failed - " + result.get_data(as_text=True))
    resultJSON = json.loads(result.get_data(as_text=True))
    
    expectedResult = copy.deepcopy(newUserDICT)
    del expectedResult["mainTenant"]
    expectedResult["TenantRoles"] = [{"TenantName": masterTenantName, "ThisTenantRoles": [DefaultHasAccountRole]}]
    expectedResult["other_data"] = {"createdBy": "adminapi/users/post"}
    
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON, expectedResult, ["associatedPersonGUIDs", "ObjectVersion", "creationDateTime", "lastUpdateDateTime"], msg='JSON of created User is not the same')
    self.assertEqual(resultJSON["ObjectVersion"],"2")

  def test_createNewUserWithNoRolesUsingAdminAPI(self):
    newUserDICT = {
      "UserID": "testUserID@TestUser",
      "known_as": "testUserID"
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/users', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newUserDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 201, msg="Create user failed - " + result.get_data(as_text=True))
    resultJSON = json.loads(result.get_data(as_text=True))
    
    expectedResult = copy.deepcopy(newUserDICT)
    expectedResult["TenantRoles"] = []
    expectedResult["other_data"] = {"createdBy": "adminapi/users/post"}
    
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON, expectedResult, ["associatedPersonGUIDs", "ObjectVersion", "creationDateTime", "lastUpdateDateTime"], msg='JSON of created User is not the same')
    self.assertEqual(resultJSON["ObjectVersion"],"1")

  def test_createNewUserInvalidTenantUsingAdminAPI(self):
    newUserDICT = {
      "UserID": "testUserID@TestUser",
      "known_as": "testUserID",
      "mainTenant": "someinvalidtenantname"
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/users', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newUserDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg="Create user should have failed - " + result.get_data(as_text=True))

  def test_createNewUserInvalidemptyDict(self):
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/users', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps({}), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg="Create user should have failed - " + result.get_data(as_text=True))

  #create user with no userID
  def test_createNewUserInvalidTenantUsingAdminAPI(self):
    newUserDICT = {
      "known_as": "testUserID",
      "mainTenant": "someinvalidtenantname"
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/users', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newUserDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg="Create user should have failed - " + result.get_data(as_text=True))
  
  #create user with duplicate userID as existing fails
  def test_createNewUserWithDuplicateIDFails(self):
    newUserDICT = {
      "UserID": appObj.defaultUserGUID,
      "known_as": "admin"
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/users', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newUserDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg="Create user did not fail - " + result.get_data(as_text=True))

  def test_deleteUserWithNoPersonRecords(self):
    #Create a user with it's person
    # delete the person record (deleting person records on their own won't result in user getting deleted)
    # then delete the user record
    tenantDict = self.setupTenantForTesting(tenantWithNoAuthProviders, True, True)
    createdAuthProvGUID = tenantDict['AuthProviders'][0]['guid']
    createdAuthSalt = tenantDict['AuthProviders'][0]['saltForPasswordHashing']

    registerJSON = {
      "authProviderGUID": createdAuthProvGUID,
      "credentialJSON": { 
        "username": "TTT", 
        "password": self.getDefaultHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(createdAuthSalt)
       }
    }
    registerResult = self.testClient.put(
      self.loginAPIPrefix + '/' + tenantDict['Name'] + '/register', 
      data=json.dumps(registerJSON), 
      content_type='application/json'
    )
    self.assertEqual(registerResult.status_code, 201, msg="Registration failed - " + registerResult.get_data(as_text=True))
    resultJSON = json.loads(registerResult.get_data(as_text=True))
    createdUserID = resultJSON["UserID"]
    associatedPersonGUID = resultJSON["associatedPersonGUIDs"][0]
    
    #In order to delete the person we need it's objectversion
    personGetResult = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/persons/' + associatedPersonGUID, headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(personGetResult.status_code, 200)
    personGetResultJSON = json.loads(personGetResult.get_data(as_text=True))
    
    print("About to delete the person")
    result = self.testClient.delete(
      self.adminAPIPrefix + '/' + masterTenantName + '/persons/' + associatedPersonGUID, 
      headers={ jwtHeaderName: self.getNormalJWTToken(), objectVersionHeaderName: personGetResultJSON['ObjectVersion']}
    )
    self.assertEqual(result.status_code, 200, msg="Delete person failed - " + result.get_data(as_text=True)) 
    print("Person deleted now deleting user")
    result = self.testClient.delete(
      self.adminAPIPrefix + '/' + masterTenantName + '/users/' + createdUserID, 
      headers={ jwtHeaderName: self.getNormalJWTToken(), objectVersionHeaderName: tenantDict['ObjectVersion']}
    )
    self.assertEqual(result.status_code, 200, msg="Delete user failed - " + result.get_data(as_text=True)) 

    #Try and retrieve the deleted user
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/users/' + createdUserID, headers={ jwtHeaderName: self.getNormalJWTToken()})
    #print(result.get_data(as_text=True))
    self.assertEqual(result.status_code, 404, msg="User still in system")    
    
  