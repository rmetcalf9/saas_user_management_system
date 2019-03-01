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

#Test User Person Links functoins of the admin API

userPersonLinkApiPath="/userpersonlinks/"

class test_adminAPIUserPersonLinks(parent_test_api):
  def assertUserPersonLinkExists(self, UserID, personGUID):
    l = getListOfUserIDsForPersonNoTenantCheck(appObj, personGUID)
    self.assertTrue(UserID in l, msg="UserPersonLink dosen't exsit but it should (1)")
    userObj = GetUser(appObj, UserID)
    if userObj is None:
      self.assertFalse(True, msg="User not found but they should have an UserPersonLink")
    self.assertTrue(personGUID in userObj._associatedPersonsList, msg="UserPersonLink dosen't exsit but it should (2)")

  def assertUserPersonLinkDosentExists(self, UserID, personGUID):
    l = getListOfUserIDsForPersonNoTenantCheck(appObj, personGUID)
    self.assertFalse(UserID in l, msg="UserPersonLink dosen't exsit but it should (1)")
    userObj = GetUser(appObj, UserID)
    if userObj is None:
      return
    self.assertFalse(personGUID in userObj._associatedPersonsList, msg="UserPersonLink dosen't exsit but it should (2)")

  def test_createUserPersonLink(self):
    newPerson = self.createPersonAndReturnDICT()
    newauthDICT = {
      "UserID": appObj.defaultUserGUID,
      "personGUID": newPerson['guid']
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + userPersonLinkApiPath + newauthDICT["UserID"] + '/' + newauthDICT["personGUID"], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newauthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 201, msg="Create auth failed - " + result.get_data(as_text=True))
    self.assertUserPersonLinkExists(newauthDICT["UserID"], newauthDICT["personGUID"])

  def test_personInPayloadNotMatchingURL(self):
    newPerson = self.createPersonAndReturnDICT()
    newauthDICT = {
      "UserID": appObj.defaultUserGUID,
      "personGUID": newPerson['guid']
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + userPersonLinkApiPath + newauthDICT["UserID"] + '/' + 'XX' + newauthDICT["personGUID"], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newauthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg="Create auth should have failed - " + result.get_data(as_text=True))
    self.assertUserPersonLinkDosentExists(newauthDICT["UserID"], newauthDICT["personGUID"])

  def test_userInPayloadNotMatchingURL(self):
    newPerson = self.createPersonAndReturnDICT()
    newauthDICT = {
      "UserID": appObj.defaultUserGUID,
      "personGUID": newPerson['guid']
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + userPersonLinkApiPath + 'XX' + newauthDICT["UserID"] + '/' + newauthDICT["personGUID"], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newauthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg="Create auth should have failed - " + result.get_data(as_text=True))
    self.assertUserPersonLinkDosentExists(newauthDICT["UserID"], newauthDICT["personGUID"])

  def test_createUserPersonLinkPersonInvalid(self):
    newauthDICT = {
      "UserID": appObj.defaultUserGUID,
      "personGUID": 'INVALID_PERSON'
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + userPersonLinkApiPath + newauthDICT["UserID"] + '/' + newauthDICT["personGUID"], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newauthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 404, msg="Create auth should have failed - " + result.get_data(as_text=True))
    self.assertUserPersonLinkDosentExists(newauthDICT["UserID"], newauthDICT["personGUID"])

  def test_createUserPersonLinkUserInvalid(self):
    newPerson = self.createPersonAndReturnDICT()
    newauthDICT = {
      "UserID": 'InvalidUser',
      "personGUID": newPerson['guid']
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + userPersonLinkApiPath + newauthDICT["UserID"] + '/' + newauthDICT["personGUID"], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newauthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 404, msg="Create auth should have failed - " + result.get_data(as_text=True))
    self.assertUserPersonLinkDosentExists(newauthDICT["UserID"], newauthDICT["personGUID"])

  def test_createUserPersonLinkAlreadyExists(self):
    newPerson = self.createPersonAndReturnDICT()
    newauthDICT = {
      "UserID": appObj.defaultUserGUID,
      "personGUID": "FORCED-CONSTANT-TESTING-PERSON-GUID"
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + userPersonLinkApiPath + newauthDICT["UserID"] + '/' + newauthDICT["personGUID"], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newauthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg="Create auth should have failed - " + result.get_data(as_text=True))
    self.assertUserPersonLinkExists(newauthDICT["UserID"], newauthDICT["personGUID"])

  def test_deleteUserPersonLink(self):
    newPerson = self.createPersonAndReturnDICT()
    newauthDICT = {
      "UserID": appObj.defaultUserGUID,
      "personGUID": newPerson['guid']
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + userPersonLinkApiPath + newauthDICT["UserID"] + '/' + newauthDICT["personGUID"], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newauthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 201, msg="Create auth failed - " + result.get_data(as_text=True))

    result = self.testClient.delete(
      self.adminAPIPrefix + '/' + masterTenantName + userPersonLinkApiPath + newauthDICT["UserID"] + '/' + newauthDICT["personGUID"], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 200, msg="Delete auth failed - " + result.get_data(as_text=True))
    self.assertUserPersonLinkDosentExists(newauthDICT["UserID"], newauthDICT["personGUID"])
    
  def test_deleteUserPersonLinkPersonInvalid(self):
    newPerson = self.createPersonAndReturnDICT()
    newauthDICT = {
      "UserID": appObj.defaultUserGUID,
      "personGUID": newPerson['guid']
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + userPersonLinkApiPath + newauthDICT["UserID"] + '/' + newauthDICT["personGUID"], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newauthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 201, msg="Create auth failed - " + result.get_data(as_text=True))

    result = self.testClient.delete(
      self.adminAPIPrefix + '/' + masterTenantName + userPersonLinkApiPath + newauthDICT["UserID"] + '/' + newauthDICT["personGUID"]  + 'XX', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg="Delete should have failed - " + result.get_data(as_text=True))
  
  def test_deleteUserPersonLinkUserInvalid(self):
    newPerson = self.createPersonAndReturnDICT()
    newauthDICT = {
      "UserID": appObj.defaultUserGUID,
      "personGUID": newPerson['guid']
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + userPersonLinkApiPath + newauthDICT["UserID"] + '/' + newauthDICT["personGUID"], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newauthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 201, msg="Create auth failed - " + result.get_data(as_text=True))

    result = self.testClient.delete(
      self.adminAPIPrefix + '/' + masterTenantName + userPersonLinkApiPath + newauthDICT["UserID"] + 'XX' + '/' + newauthDICT["personGUID"], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg="Delete should have failed - " + result.get_data(as_text=True))

  def test_deleteUserPersonLinkDosntExist(self):
    newPerson = self.createPersonAndReturnDICT()
    newauthDICT = {
      "UserID": appObj.defaultUserGUID,
      "personGUID": newPerson['guid']
    }

    result = self.testClient.delete(
      self.adminAPIPrefix + '/' + masterTenantName + userPersonLinkApiPath + newauthDICT["UserID"] + '/' + newauthDICT["personGUID"], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg="Delete auth should have failed - " + result.get_data(as_text=True))
    self.assertUserPersonLinkDosentExists(newauthDICT["UserID"], newauthDICT["personGUID"])  
    

