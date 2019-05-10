from test_loginAPI import test_api as parent_test_api
#from TestHelperSuperClass import testHelperAPIClient, env, tenantWithNoAuthProviders, sampleInternalAuthProv001_CREATE
from TestHelperSuperClass import tenantWithNoAuthProviders, sampleInternalAuthProv001_CREATE, env, internalUSerSufix, sampleInternalAuthProv001_CREATE_WithAllowUserCreation, getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse
import json
from appObj import appObj
import datetime
import pytz
#from datetime import timedelta, datetime
#from dateutil.parser import parse
import copy
from constants import masterTenantName, jwtHeaderName, objectVersionHeaderName, DefaultHasAccountRole

class test_loginapi_register(parent_test_api):

  def test_registerNewUser(self):
    testDateTime = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testDateTime)
    tenantDict = self.createTenantWithAuthProvider(tenantWithNoAuthProviders, True, sampleInternalAuthProv001_CREATE_WithAllowUserCreation)
  
    createdAuthProvGUID = tenantDict['AuthProviders'][0]['guid']
    createdAuthSalt = tenantDict['AuthProviders'][0]['saltForPasswordHashing']
    
    userName = "testSetUserName"
    password = "delkjgn4rflkjwned"
    
    registerResultJSON = self.registerInternalUser(tenantWithNoAuthProviders['Name'], userName, password, tenantDict['AuthProviders'][0])
    
    expectedUserDICT = {
      "UserID": userName + internalUSerSufix,
      "known_as": userName,
      "ObjectVersion": "2",
      "TenantRoles": [{
        "TenantName": tenantWithNoAuthProviders['Name'],
        "ThisTenantRoles": [DefaultHasAccountRole]
      }],
      "creationDateTime": testDateTime.isoformat(),
      "lastUpdateDateTime": testDateTime.isoformat()
    }
    
    self.assertFalse('other_data' in registerResultJSON, msg="Found other_data in user registerResultJSON")
    
    self.assertJSONStringsEqualWithIgnoredKeys(registerResultJSON, expectedUserDICT, ['associatedPersonGUIDs'], msg='Incorrect response from registration')
    self.assertEqual(len(registerResultJSON['associatedPersonGUIDs']),1)

    loginResultJSON = self.loginAsUser(
      tenantWithNoAuthProviders['Name'], 
      self.getTenantInternalAuthProvDict(tenantWithNoAuthProviders['Name']), 
      userName, 
      password
    )

    self.assertFalse('other_data' in loginResultJSON)
    
    #Test other_data is filled in. This is only returned in the admin API get function so can't use login api to view
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/users/' + userName + internalUSerSufix, headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)

    userGetResultDICT = json.loads(result.get_data(as_text=True))
    expectedResult = {
      'UserID': userName + internalUSerSufix, 
      'known_as': userName, 
      'TenantRoles': [
        {
          'TenantName': tenantWithNoAuthProviders['Name'], 
          'ThisTenantRoles': [DefaultHasAccountRole]
        }
      ], 
      'other_data': {
        "createdBy": "loginapi/register"
      }, 
      'ObjectVersion': '2',
      "creationDateTime": testDateTime.isoformat(),
      "lastUpdateDateTime": testDateTime.isoformat(),
      "associatedPersonGUIDs": registerResultJSON['associatedPersonGUIDs']
    }
    self.assertJSONStringsEqualWithIgnoredKeys(userGetResultDICT, expectedResult, [], msg='Admin API User data wrong')


  def test_registerNewUserTenantFail(self):
    tenantDict = self.createTenantWithAuthProvider(tenantWithNoAuthProviders, False, sampleInternalAuthProv001_CREATE)
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
    # 401 Unauthorized response
    self.assertEqual(registerResult.status_code, 401, msg="Registration passed but should have failed")

  def test_registerNewUserAuthProvFail(self):
    tenantDict = self.createTenantWithAuthProvider(tenantWithNoAuthProviders, True, sampleInternalAuthProv001_CREATE)
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
    # 401 Unauthorized response
    self.assertEqual(registerResult.status_code, 401, msg="Registration passed but should have failed")

  def test_registerWithBadCredentialJSON(self):
    tenantDict = self.createTenantWithAuthProvider(tenantWithNoAuthProviders, True, sampleInternalAuthProv001_CREATE_WithAllowUserCreation)
    createdAuthProvGUID = tenantDict['AuthProviders'][0]['guid']
    createdAuthSalt = tenantDict['AuthProviders'][0]['saltForPasswordHashing']
    
    userName = "testSetUserName"
    
    registerJSON = {
      "authProviderGUID": createdAuthProvGUID,
      "credentialJSON": { 
        "usernameXX": userName, 
        "passwordYY": self.getDefaultHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(createdAuthSalt)
       }
    }
    
    registerResult = self.testClient.put(
      self.loginAPIPrefix + '/' + tenantWithNoAuthProviders['Name'] + '/register', 
      data=json.dumps(registerJSON), 
      content_type='application/json'
    )
    # 400 Unauthorized response
    self.assertEqual(registerResult.status_code, 400, msg="Bad credential JSON not rejected")

  def test_registerTwoUsersWithSameNameSecondShouldFail(self):
    tenantDict = self.createTenantWithAuthProvider(tenantWithNoAuthProviders, True, sampleInternalAuthProv001_CREATE_WithAllowUserCreation)
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
    self.assertEqual(registerResult.status_code, 201, msg="First user not created")
    
    registerResult2 = self.testClient.put(
      self.loginAPIPrefix + '/' + tenantWithNoAuthProviders['Name'] + '/register', 
      data=json.dumps(copy.deepcopy(registerJSON)),
      content_type='application/json'
    )
    resultJSON = json.loads(registerResult2.get_data(as_text=True))
    self.assertEqual(registerResult2.status_code, 400, msg="Second user with conflicting name should fail")
    self.assertEqual(resultJSON['message'], "That username is already in use", msg="Incorrect error message")

  def test_registerMutipleUsersWithDifferentNamesWorks(self):
    tenantDict = self.createTenantWithAuthProvider(tenantWithNoAuthProviders, True, sampleInternalAuthProv001_CREATE_WithAllowUserCreation)
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
    for a in range(1,5):
      aa = copy.deepcopy(registerJSON)
      aa['credentialJSON']['username'] = 'testUser' + str(a)
      print("Creating user:",aa['credentialJSON']['username'])
      registerResult = self.testClient.put(
        self.loginAPIPrefix + '/' + tenantWithNoAuthProviders['Name'] + '/register', 
        data=json.dumps(aa),
        content_type='application/json'
      )
      self.assertEqual(registerResult.status_code, 201, msg="User not created")
    
  def test_ableToReuseDeletedUsername(self):
    tenantDict = self.createTenantWithAuthProvider(tenantWithNoAuthProviders, True, sampleInternalAuthProv001_CREATE_WithAllowUserCreation)
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
    self.assertEqual(registerResult.status_code, 201, msg="User not created")
    resultJSON = json.loads(registerResult.get_data(as_text=True))
    createdUserID = resultJSON["UserID"]
    
    deleteresult = self.testClient.delete(
      self.adminAPIPrefix + '/' + masterTenantName + '/users/' + createdUserID, 
      headers={ jwtHeaderName: self.getNormalJWTToken(), objectVersionHeaderName: resultJSON['ObjectVersion']}
    )
    self.assertEqual(deleteresult.status_code, 200, msg="Delete user failed - " + deleteresult.get_data(as_text=True)) 

    registerResult = self.testClient.put(
      self.loginAPIPrefix + '/' + tenantWithNoAuthProviders['Name'] + '/register', 
      data=json.dumps(registerJSON),
      content_type='application/json'
    )
    self.assertEqual(registerResult.status_code, 201, msg="creation after delete failed" + registerResult.get_data(as_text=True))

  def test_unableToLoginAsDeletedUser(self):
    tenantDict = self.createTenantWithAuthProvider(tenantWithNoAuthProviders, True, sampleInternalAuthProv001_CREATE_WithAllowUserCreation)
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
    self.assertEqual(registerResult.status_code, 201, msg="User not created")
    resultJSON = json.loads(registerResult.get_data(as_text=True))
    createdUserID = resultJSON["UserID"]
    
    loginJSON = {
      "authProviderGUID": createdAuthProvGUID,
      "credentialJSON": { 
        "username": userName, 
        "password": self.getDefaultHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(createdAuthSalt)
       }
    }
    loginResult = self.testClient.post(
      self.loginAPIPrefix + '/' + tenantWithNoAuthProviders['Name'] + '/authproviders', 
      data=json.dumps(loginJSON), 
      content_type='application/json'
    )
    self.assertEqual(loginResult.status_code, 200, msg="Unable to login as newly registered user - " + loginResult.get_data(as_text=True))
    
    deleteresult = self.testClient.delete(
      self.adminAPIPrefix + '/' + masterTenantName + '/users/' + createdUserID, 
      headers={ jwtHeaderName: self.getNormalJWTToken(), objectVersionHeaderName: resultJSON['ObjectVersion']}
    )
    self.assertEqual(deleteresult.status_code, 200, msg="Delete user failed - " + deleteresult.get_data(as_text=True)) 

    loginResult = self.testClient.post(
      self.loginAPIPrefix + '/' + tenantWithNoAuthProviders['Name'] + '/authproviders', 
      data=json.dumps(loginJSON), 
      content_type='application/json'
    )
    self.assertEqual(loginResult.status_code, 401, msg="Managed to login as a deleted user")
    
  def test_registerNewUserFailsWithDuplicateUsername(self):
    tenantDict = self.createTenantWithAuthProvider(tenantWithNoAuthProviders, True, sampleInternalAuthProv001_CREATE_WithAllowUserCreation)
  
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
    
    registerResult = self.testClient.put(
      self.loginAPIPrefix + '/' + tenantWithNoAuthProviders['Name'] + '/register', 
      data=json.dumps(registerJSON), 
      content_type='application/json'
    )
    self.assertEqual(registerResult.status_code, 400, msg="Registration of second user with same name did not fail")

  def test_registerNewUserFailsWithDuplicateUsernameDifferByCase(self):
    tenantDict = self.createTenantWithAuthProvider(tenantWithNoAuthProviders, True, sampleInternalAuthProv001_CREATE_WithAllowUserCreation)
  
    createdAuthProvGUID = tenantDict['AuthProviders'][0]['guid']
    createdAuthSalt = tenantDict['AuthProviders'][0]['saltForPasswordHashing']
    
    userName = "testSetUserName"
    userName2 = "testSetUserNaME"
    
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
    
    registerJSON2 = copy.deepcopy(registerJSON)
    registerJSON2["credentialJSON"]["username"] = userName2
    
    registerResult = self.testClient.put(
      self.loginAPIPrefix + '/' + tenantWithNoAuthProviders['Name'] + '/register', 
      data=json.dumps(registerJSON), 
      content_type='application/json'
    )
    self.assertEqual(registerResult.status_code, 400, msg="Registration of second user with same name did not fail " + registerResult.get_data(as_text=True) )
    