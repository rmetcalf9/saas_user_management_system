from datetime import datetime, timedelta
import pytz
from TestHelperSuperClass import testHelperAPIClient, env, tenantWithNoAuthProviders, sampleInternalAuthProv001_CREATE, internalUSerSufix, sampleInternalAuthProv001_CREATE_WithAllowUserCreation
from appObj import appObj
from constants import masterTenantName, jwtHeaderName, objectVersionHeaderName, DefaultHasAccountRole, masterTenantDefaultSystemAdminRole
from test_adminAPI import test_api as parent_test_api
import json
import copy

#Test the filtering of the users request API


class test_adminAPIUserFilter(parent_test_api):
  userUIDNum = 0
  testTenantDict = None

  def createUserUsingAdminAPI(self):
    self.userUIDNum = self.userUIDNum + 1
    knownAs = "tu" + str(self.userUIDNum)
    newUserDICT = {
      "UserID": knownAs + "" + "@TestUser",
      "known_as": knownAs
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/users', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newUserDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 201, msg="Create user failed - " + result.get_data(as_text=True))
    
  def createUserUsingLoginRegisterAPI(self):
    if self.testTenantDict is None:
      self.testTenantDict = self.createTenantWithAuthProvider(tenantWithNoAuthProviders, True, sampleInternalAuthProv001_CREATE_WithAllowUserCreation)

    createdAuthProvGUID = self.testTenantDict['AuthProviders'][0]['guid']
    createdAuthSalt = self.testTenantDict['AuthProviders'][0]['saltForPasswordHashing']

    self.userUIDNum = self.userUIDNum + 1
    userName = "regUser" + str(self.userUIDNum)
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
    self.assertEqual(registerResult.status_code, 201, msg="Registration failed - " + registerResult.get_data(as_text=True))

  
  def injectTestRecords(self):
    for a in range(0, 10):
      self.createUserUsingAdminAPI()
    for a in range(0, 10):
      self.createUserUsingLoginRegisterAPI()

  def test_getUsersWithNoFilter(self):
    self.injectTestRecords()
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/users', headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    
    resultJSON = json.loads(result.get_data(as_text=True))
    self.assertEqual(resultJSON['pagination']['total'], 21, msg="Wrong number of users returned")
  
    creationMethodStats = {}
    for cur in resultJSON['result']:
      if cur['other_data']['createdBy'] in creationMethodStats.keys():
        creationMethodStats[cur['other_data']['createdBy']] = creationMethodStats[cur['other_data']['createdBy']] + 1
      else:
        creationMethodStats[cur['other_data']['createdBy']] = 1
    self.assertEqual(creationMethodStats,{'init/CreateMasterTenant': 1, 'adminapi/users/post': 10, 'loginapi/register': 10}, msg='Wrong number of users created or wrong method')
      
  def test_getMainUserByCreationMethod(self):
    self.injectTestRecords()
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/users?query=init/CreateMasterTenant', headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    
    resultJSON = json.loads(result.get_data(as_text=True))
    self.assertEqual(resultJSON['pagination']['total'], 1, msg="Wrong number of users returned")
    
  def test_getUserFilterForExistingUserID(self):
    self.injectTestRecords()
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/users?query=' + appObj.defaultUserGUID, headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    
    resultJSON = json.loads(result.get_data(as_text=True))
    self.assertEqual(resultJSON['pagination']['total'], 1, msg="Wrong number of users returned")
    

  def test_getUserFilterForExistingUserID(self):
    self.injectTestRecords()
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/users?query=JohnSmith324', headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    
    resultJSON = json.loads(result.get_data(as_text=True))
    self.assertEqual(resultJSON['pagination']['total'], 0, msg="Wrong number of users returned")
    
