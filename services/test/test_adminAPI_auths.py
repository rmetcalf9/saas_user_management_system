from datetime import datetime, timedelta
import pytz
from TestHelperSuperClass import testHelperAPIClient, env, tenantWithNoAuthProviders, sampleInternalAuthProv001_CREATE, internalUSerSufix
from appObj import appObj
from constants import masterTenantName, jwtHeaderName, objectVersionHeaderName, DefaultHasAccountRole, masterTenantDefaultSystemAdminRole
from test_adminAPI import test_api as parent_test_api
from test_adminAPI_users import defaultUserData
import json
import copy
from userPersonCommon import getListOfUserIDsForPersonNoTenantCheck, GetUser

#Test Auth functoins of the admin API

class test_adminAPIAuths(parent_test_api):
  def assertAuthExists(self, UserID, personGUID):
    l = getListOfUserIDsForPersonNoTenantCheck(appObj, personGUID)
    self.assertTrue(UserID in l, msg="Auth dosen't exsit but it should (1)")
    userObj = GetUser(appObj, UserID)
    if userObj is None:
      self.assertFalse(True, msg="User not found but they should have an auth")
    self.assertTrue(personGUID in userObj._associatedPersonsList, msg="Auth dosen't exsit but it should (2)")

  def assertAuthDosentExists(self, UserID, personGUID):
    l = getListOfUserIDsForPersonNoTenantCheck(appObj, personGUID)
    self.assertFalse(UserID in l, msg="Auth dosen't exsit but it should (1)")
    userObj = GetUser(appObj, UserID)
    if userObj is None:
      return
    self.assertFalse(personGUID in userObj._associatedPersonsList, msg="Auth dosen't exsit but it should (2)")

  def test_createAuth(self):
    newPerson = self.createPersonAndReturnDICT()
    newauthDICT = {
      "UserID": appObj.defaultUserGUID,
      "personGUID": newPerson['guid']
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths/' + newauthDICT["UserID"] + '/' + newauthDICT["personGUID"], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newauthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 201, msg="Create auth failed - " + result.get_data(as_text=True))
    self.assertAuthExists(newauthDICT["UserID"], newauthDICT["personGUID"])

  def test_personInPayloadNotMatchingURL(self):
    newPerson = self.createPersonAndReturnDICT()
    newauthDICT = {
      "UserID": appObj.defaultUserGUID,
      "personGUID": newPerson['guid']
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths/' + newauthDICT["UserID"] + '/' + 'XX' + newauthDICT["personGUID"], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newauthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg="Create auth should have failed - " + result.get_data(as_text=True))
    self.assertAuthDosentExists(newauthDICT["UserID"], newauthDICT["personGUID"])

  def test_userInPayloadNotMatchingURL(self):
    newPerson = self.createPersonAndReturnDICT()
    newauthDICT = {
      "UserID": appObj.defaultUserGUID,
      "personGUID": newPerson['guid']
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths/' + 'XX' + newauthDICT["UserID"] + '/' + newauthDICT["personGUID"], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newauthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg="Create auth should have failed - " + result.get_data(as_text=True))
    self.assertAuthDosentExists(newauthDICT["UserID"], newauthDICT["personGUID"])

  def test_createAuthPersonInvalid(self):
    newauthDICT = {
      "UserID": appObj.defaultUserGUID,
      "personGUID": 'INVALID_PERSON'
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths/' + newauthDICT["UserID"] + '/' + newauthDICT["personGUID"], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newauthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 404, msg="Create auth should have failed - " + result.get_data(as_text=True))
    self.assertAuthDosentExists(newauthDICT["UserID"], newauthDICT["personGUID"])

  def test_createAuthUserInvalid(self):
    newPerson = self.createPersonAndReturnDICT()
    newauthDICT = {
      "UserID": 'InvalidUser',
      "personGUID": newPerson['guid']
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths/' + newauthDICT["UserID"] + '/' + newauthDICT["personGUID"], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newauthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 404, msg="Create auth should have failed - " + result.get_data(as_text=True))
    self.assertAuthDosentExists(newauthDICT["UserID"], newauthDICT["personGUID"])

  def test_createAuthAlreadyExists(self):
    newPerson = self.createPersonAndReturnDICT()
    newauthDICT = {
      "UserID": appObj.defaultUserGUID,
      "personGUID": "FORCED-CONSTANT-TESTING-PERSON-GUID"
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths/' + newauthDICT["UserID"] + '/' + newauthDICT["personGUID"], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newauthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg="Create auth should have failed - " + result.get_data(as_text=True))
    self.assertAuthExists(newauthDICT["UserID"], newauthDICT["personGUID"])

  def test_deleteAuth(self):
    newPerson = self.createPersonAndReturnDICT()
    newauthDICT = {
      "UserID": appObj.defaultUserGUID,
      "personGUID": newPerson['guid']
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths/' + newauthDICT["UserID"] + '/' + newauthDICT["personGUID"], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newauthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 201, msg="Create auth failed - " + result.get_data(as_text=True))

    result = self.testClient.delete(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths/' + newauthDICT["UserID"] + '/' + newauthDICT["personGUID"], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 200, msg="Delete auth failed - " + result.get_data(as_text=True))
    self.assertAuthDosentExists(newauthDICT["UserID"], newauthDICT["personGUID"])
    
  def test_deleteAuthPersonInvalid(self):
    newPerson = self.createPersonAndReturnDICT()
    newauthDICT = {
      "UserID": appObj.defaultUserGUID,
      "personGUID": newPerson['guid']
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths/' + newauthDICT["UserID"] + '/' + newauthDICT["personGUID"], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newauthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 201, msg="Create auth failed - " + result.get_data(as_text=True))

    result = self.testClient.delete(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths/' + newauthDICT["UserID"] + '/' + newauthDICT["personGUID"]  + 'XX', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg="Delete should have failed - " + result.get_data(as_text=True))
  
  def test_deleteAuthUserInvalid(self):
    newPerson = self.createPersonAndReturnDICT()
    newauthDICT = {
      "UserID": appObj.defaultUserGUID,
      "personGUID": newPerson['guid']
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths/' + newauthDICT["UserID"] + '/' + newauthDICT["personGUID"], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newauthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 201, msg="Create auth failed - " + result.get_data(as_text=True))

    result = self.testClient.delete(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths/' + newauthDICT["UserID"] + 'XX' + '/' + newauthDICT["personGUID"], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg="Delete should have failed - " + result.get_data(as_text=True))

  def test_deleteAuthDosntExist(self):
    newPerson = self.createPersonAndReturnDICT()
    newauthDICT = {
      "UserID": appObj.defaultUserGUID,
      "personGUID": newPerson['guid']
    }

    result = self.testClient.delete(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths/' + newauthDICT["UserID"] + '/' + newauthDICT["personGUID"], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg="Delete auth should have failed - " + result.get_data(as_text=True))
    self.assertAuthDosentExists(newauthDICT["UserID"], newauthDICT["personGUID"])  
    

