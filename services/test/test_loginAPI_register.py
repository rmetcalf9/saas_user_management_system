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

  def test_registerNewUser(self):
    tenantWithUserCreation = copy.deepcopy(tenantWithNoAuthProviders)
    tenantWithUserCreation['Name'] = 'tenantWithAllowUserCreation'
    tenantWithUserCreation['AllowUserCreation'] = True
    authProvCreateWithUserCreation = copy.deepcopy(sampleInternalAuthProv001_CREATE)
    authProvCreateWithUserCreation['AllowUserCreation'] = True
    tenantDict = self.createTenantForTestingWithMutipleAuthProviders(tenantWithUserCreation, [authProvCreateWithUserCreation])
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
      self.loginAPIPrefix + '/' + tenantWithUserCreation['Name'] + '/register', 
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
      self.loginAPIPrefix + '/' + tenantWithUserCreation['Name'] + '/authproviders', 
      data=json.dumps(loginJSON), 
      content_type='application/json'
    )
    self.assertEqual(loginResult.status_code, 200, msg="Unable to login as newly registered user - " + loginResult.get_data(as_text=True))

  def test_registerNewUserTenantFail(self):
    tenantWithUserCreation = copy.deepcopy(tenantWithNoAuthProviders)
    tenantWithUserCreation['Name'] = 'tenantWithAllowUserCreation'
    tenantWithUserCreation['AllowUserCreation'] = False
    authProvCreateWithUserCreation = copy.deepcopy(sampleInternalAuthProv001_CREATE)
    authProvCreateWithUserCreation['AllowUserCreation'] = True
    tenantDict = self.createTenantForTestingWithMutipleAuthProviders(tenantWithUserCreation, [authProvCreateWithUserCreation])
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
      self.loginAPIPrefix + '/' + tenantWithUserCreation['Name'] + '/register', 
      data=json.dumps(registerJSON), 
      content_type='application/json'
    )
    # 401 Unauthorized response
    self.assertEqual(registerResult.status_code, 401, msg="Registration passed but should have failed")

  def test_registerNewUserAuthProvFail(self):
    tenantWithUserCreation = copy.deepcopy(tenantWithNoAuthProviders)
    tenantWithUserCreation['Name'] = 'tenantWithAllowUserCreation'
    tenantWithUserCreation['AllowUserCreation'] = True
    authProvCreateWithUserCreation = copy.deepcopy(sampleInternalAuthProv001_CREATE)
    authProvCreateWithUserCreation['AllowUserCreation'] = False
    tenantDict = self.createTenantForTestingWithMutipleAuthProviders(tenantWithUserCreation, [authProvCreateWithUserCreation])
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
      self.loginAPIPrefix + '/' + tenantWithUserCreation['Name'] + '/register', 
      data=json.dumps(registerJSON), 
      content_type='application/json'
    )
    # 401 Unauthorized response
    self.assertEqual(registerResult.status_code, 401, msg="Registration passed but should have failed")

  #TODO Try and register with invalid credential data
  # 400 Bad Request response

  #TODO Try and register two users with same username
  # 400 Bad REquest response with message