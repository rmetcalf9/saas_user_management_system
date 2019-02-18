from test_loginAPI import test_api as parent_test_api
#from TestHelperSuperClass import testHelperAPIClient, env, tenantWithNoAuthProviders, sampleInternalAuthProv001_CREATE
from TestHelperSuperClass import tenantWithNoAuthProviders, sampleInternalAuthProv001_CREATE, env
import json
#from appObj import appObj
#import pytz
#from datetime import timedelta, datetime
#from dateutil.parser import parse
import copy
from constants import masterTenantName
#from constants import masterTenantName, masterTenantDefaultDescription, masterTenantDefaultAuthProviderMenuText, masterTenantDefaultAuthProviderMenuIconLink


class test_loginapi_register(parent_test_api):  
  def setupTenantForTesting(self, tenantBase, tenantUserCreation, AuthUserCreation):
    tenantWithUserCreation = copy.deepcopy(tenantBase)
    tenantWithUserCreation['AllowUserCreation'] = tenantUserCreation
    authProvCreateWithUserCreation = copy.deepcopy(sampleInternalAuthProv001_CREATE)
    authProvCreateWithUserCreation['AllowUserCreation'] = AuthUserCreation
    return self.createTenantForTestingWithMutipleAuthProviders(tenantWithUserCreation, [authProvCreateWithUserCreation])

  def test_registerNewUser(self):
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

  def test_registerNewUserTenantFail(self):
    tenantDict = self.setupTenantForTesting(tenantWithNoAuthProviders, False, True)
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
    tenantDict = self.setupTenantForTesting(tenantWithNoAuthProviders, True, False)
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
    tenantDict = self.setupTenantForTesting(tenantWithNoAuthProviders, True, True)
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
    
