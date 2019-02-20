from datetime import datetime, timedelta
import pytz
from TestHelperSuperClass import testHelperAPIClient, env, tenantWithNoAuthProviders, sampleInternalAuthProv001_CREATE, internalUSerSufix
from appObj import appObj
from constants import masterTenantName, jwtHeaderName
from test_adminAPI import test_api as parent_test_api
import json
import copy

#Test user functoins of the admin API

defaultUserData = {
  'UserID': appObj.defaultUserGUID,
  'known_as': env['APIAPP_DEFAULTHOMEADMINUSERNAME'],
  'TenantRoles': [{
    'TenantName': masterTenantName,
    'ThisTenantRoles': ['systemadmin', 'hasaccount']
  }],
  'other_data': {},
  'ObjectVersion': "3"
}

class test_adminAPIUsers(parent_test_api):
  def test_getDefaultListFromMasterTenant(self):
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/users', headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    
    resultJSON = json.loads(result.get_data(as_text=True))
    self.assertEqual(resultJSON['pagination']['total'],1)
    
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON['result'][0],defaultUserData, ["TenantRoles"], msg="User data mismatch")
    
    self.assertEqual(len(resultJSON['result'][0]["TenantRoles"]),1,msg="Didn't return single tenant")

    expectedTenantRolesResult = [{
      "TenantName": masterTenantName,
      "ThisTenantRoles": ['systemadmin', 'hasaccount']
    }]
    
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON['result'][0]["TenantRoles"],expectedTenantRolesResult, ["TenantRoles"], msg="Tenant Roles returned data wrong")
    
  def test_getUserListThreeTenantsAndMutipleUsers(self):
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
    
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON['result'][0],defaultUserData, ["TenantRoles"], msg="User data mismatch")
    self.assertEqual(len(resultJSON['result'][0]["TenantRoles"]),1,msg="Didn't return single tenant")
    expectedTenantRolesResult = [{
      "TenantName": masterTenantName,
      "ThisTenantRoles": ['systemadmin', 'hasaccount']
    }]
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON['result'][0]["TenantRoles"],expectedTenantRolesResult, ["TenantRoles"], msg="Tenant Roles returned data wrong")
   
    expectedResult = {
      'UserID': userName + internalUSerSufix,
      'known_as': userName,
      'other_data': {},
      'ObjectVersion': "2"
    }
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON['result'][1],expectedResult, ["TenantRoles"], msg="User data mismatch")
    self.assertEqual(len(resultJSON['result'][1]["TenantRoles"]),1,msg="Didn't return single tenant")
    expectedTenantRolesResult = [{
      "TenantName": tenantDict["Name"],
      "ThisTenantRoles": ['hasaccount']
    }]
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON['result'][1]["TenantRoles"],expectedTenantRolesResult, ["TenantRoles"], msg="Tenant Roles returned data wrong")
   
  def test_getSingleUser(self):
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/users/' + appObj.defaultUserGUID, headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)

    resultJSON = json.loads(result.get_data(as_text=True))

    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON,defaultUserData, ["TenantRoles"], msg="Returned user data")
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON["TenantRoles"],defaultUserData["TenantRoles"], [], msg="Returned user data")
    
  def test_updateUserData(self):
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
    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/users/' + appObj.defaultUserGUID, 
      data=json.dumps(newUserDICT), 
      content_type='application/json',
      headers={ jwtHeaderName: self.getNormalJWTToken()}
    )
    self.assertEqual(result.status_code, 200)
    newUserDICT['ObjectVersion'] = str(int(newUserDICT['ObjectVersion']) + 1)
    
    resultJSON = json.loads(result.get_data(as_text=True))
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON,newUserDICT, ["TenantRoles"], msg="Returned user data")
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON["TenantRoles"],newUserDICT["TenantRoles"], [], msg="Returned user data")


    result2 = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/users/' + appObj.defaultUserGUID, headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result2.status_code, 200)
    result2JSON = json.loads(result2.get_data(as_text=True))
    self.assertJSONStringsEqualWithIgnoredKeys(result2JSON,newUserDICT, ["TenantRoles"], msg="Returned user data")
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
   
