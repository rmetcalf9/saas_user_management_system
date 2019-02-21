from TestHelperSuperClass import testHelperAPIClient, env, tenantWithNoAuthProviders, sampleInternalAuthProv001_CREATE
import unittest
import json
from appObj import appObj
import pytz
from datetime import timedelta, datetime
from dateutil.parser import parse
import copy

from constants import masterTenantName, masterTenantDefaultDescription, masterTenantDefaultAuthProviderMenuText, masterTenantDefaultAuthProviderMenuIconLink



invalidTenantName="invalidtenantname"

class test_api(testHelperAPIClient):
  def loginAsDefaultUser(self):
    result = self.testClient.get(self.loginAPIPrefix + '/' + masterTenantName + '/authproviders')
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))
    masterAuthProviderGUID = resultJSON[ 'AuthProviders' ][0]['guid']
    
    loginJSON = {
      "authProviderGUID": masterAuthProviderGUID,
      "credentialJSON": { 
        "username": env['APIAPP_DEFAULTHOMEADMINUSERNAME'], 
        "password": self.getDefaultHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(resultJSON[ 'AuthProviders' ][0]['saltForPasswordHashing'])
       }
    }
    result2 = self.testClient.post(self.loginAPIPrefix + '/' + masterTenantName + '/authproviders', data=json.dumps(loginJSON), content_type='application/json')
    self.assertEqual(result2.status_code, 200)
    return json.loads(result2.get_data(as_text=True))

class test_loginapi_norm(test_api):    
  def test_loginInvalidTenantFails(self):
    result = self.testClient.get(self.loginAPIPrefix + '/' + invalidTenantName + '/authproviders')
    self.assertEqual(result.status_code, 400)
    resultJSON = json.loads(result.get_data(as_text=True))
    self.assertJSONStringsEqual(resultJSON, {"message": "Tenant not found"})

  def test_loginReturnsDefaultTenantAndAuthInfo(self):
    result = self.testClient.get(self.loginAPIPrefix + '/' + masterTenantName + '/authproviders')
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))
    
    expectedResult = {
      "Name": masterTenantName,
      "Description": masterTenantDefaultDescription, 
      "AllowUserCreation": False, 
      "AuthProviders": [{
        "guid": "1199545b-58f4-4f6e-885a-376dad1a68e9",
        "Type": "internal", 
        "MenuText": masterTenantDefaultAuthProviderMenuText, 
        "IconLink": masterTenantDefaultAuthProviderMenuIconLink, 
        "AllowUserCreation": False, 
        "ConfigJSON": "{\"userSufix\": \"@internalDataStore\"}"
      }],
      "ObjectVersion": "2"
    }
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON, expectedResult, [ 'AuthProviders' ])
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON[ 'AuthProviders' ][0], expectedResult[ 'AuthProviders' ][0], [ 'guid', 'saltForPasswordHashing' ], msg="Master tenant auth provider wrong")

  def test_sucessfulLoginAsDefaultUser(self):
    result2JSON = self.loginAsDefaultUser()
    
    result = self.testClient.get(self.loginAPIPrefix + '/' + masterTenantName + '/authproviders')
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))
    masterAuthProviderGUID = resultJSON[ 'AuthProviders' ][0]['guid']
    
    loginJSON = {
      "authProviderGUID": masterAuthProviderGUID,
      "credentialJSON": { 
        "username": env['APIAPP_DEFAULTHOMEADMINUSERNAME'], 
        "password": self.getDefaultHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(resultJSON[ 'AuthProviders' ][0]['saltForPasswordHashing'])
       }
    }
    result2 = self.testClient.post(self.loginAPIPrefix + '/' + masterTenantName + '/authproviders', data=json.dumps(loginJSON), content_type='application/json')
    self.assertEqual(result2.status_code, 200)
    result2JSON = json.loads(result2.get_data(as_text=True))

    expectedResult = {
      "userGuid": "FORCED-CONSTANT-TESTING-GUID",
      "authedPersonGuid": "Ignore",
      "ThisTenantRoles": ['systemadmin', 'hasaccount'],
      "known_as": env['APIAPP_DEFAULTHOMEADMINUSERNAME']
    }
    self.assertJSONStringsEqualWithIgnoredKeys(result2JSON, expectedResult, [ 'jwtData', 'authedPersonGuid', 'refresh' ])

    expectedResult = {
    }
    self.assertJSONStringsEqualWithIgnoredKeys(result2JSON[ 'jwtData' ], expectedResult, [ 'JWTToken','TokenExpiry' ])
    
    jwtTokenDict = self.decodeToken(result2JSON[ 'jwtData' ]['JWTToken'])
    expectedTokenDict = {
      'UserID': 'FORCED-CONSTANT-TESTING-GUID', 
      'iss': 'FORCED-CONSTANT-TESTING-GUID', 
      'TenantRoles': {
        'usersystem': ['systemadmin', 'hasaccount']
      }, 
      'exp': 1547292391,
      'authedPersonGuid': 'Ignore',
      "known_as": env['APIAPP_DEFAULTHOMEADMINUSERNAME'],
      "other_data": {}
    }
    self.assertJSONStringsEqualWithIgnoredKeys(jwtTokenDict, expectedTokenDict, [ 'exp', 'authedPersonGuid' ])
    
    #Make sure passed expiry matches token expiry
    dt = parse(result2JSON['jwtData']['TokenExpiry'])
    dateTimeObjFromJSON = dt.astimezone(pytz.utc)

    dateTimeObjFromToken = datetime.fromtimestamp(jwtTokenDict['exp'],pytz.utc)
    time_diff = (dateTimeObjFromToken - dateTimeObjFromJSON).total_seconds()
    self.assertTrue(abs(time_diff) < 1,msg="More than 1 second difference between reported expiry time and actual expiry time in token")
    
    #Make sure expiry is in the future
    expectedExpiry = datetime.now(pytz.utc) + timedelta(seconds=int(env['APIAPP_JWT_TOKEN_TIMEOUT']))

    time_diff = (expectedExpiry - dateTimeObjFromJSON).total_seconds()
    self.assertTrue(abs(time_diff) < 1,msg="Token expiry not in correct range")

    #Sucessfull login test point
    #self.assertTrue(False)
    
  def test_getMutipleIdentityResponseDefaultUser(self):
    userID1 = 'TestUser1'
    userID2 = 'TestUser2'
    InternalAuthUsername = 'ABC'
    res = self.createUserWithTwoIdentititesForOnePerson(userID1, userID2, InternalAuthUsername)
    
    
    result = self.testClient.get(self.loginAPIPrefix + '/' + masterTenantName + '/authproviders')
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))
    masterAuthProviderGUID = resultJSON[ 'AuthProviders' ][0]['guid']
    
    loginJSON = {
      ##"identityGUID": "string",
      "authProviderGUID": masterAuthProviderGUID,
      "credentialJSON": { 
        "username": InternalAuthUsername, 
        "password": env['APIAPP_DEFAULTHOMEADMINPASSWORD']
       }
    }
    result2 = self.testClient.post(self.loginAPIPrefix + '/' + masterTenantName + '/authproviders', data=json.dumps(loginJSON), content_type='application/json')
    self.assertEqual(result2.status_code, 200)
    result2JSON = json.loads(result2.get_data(as_text=True))

    user1ExcpectedResult = {
      "UserID": userID1,
      "TenantRoles": [{
        "TenantName": masterTenantName,
        "ThisTenantRoles": ["hasaccount"]
      }],
      "known_as": userID1,
      "other_data": {}
    }
    user2ExcpectedResult = {
      "UserID": userID2,
      "TenantRoles": [{
        "TenantName": masterTenantName,
        "ThisTenantRoles": ["hasaccount"]
      }],
      "known_as": userID2,
      "other_data": {}
    }
    id1Found = False
    id2Found = False

    for resultUser in result2JSON['possibleUsers']:
      if resultUser['UserID'] == userID1:
        id1Found = True
        self.assertJSONStringsEqualWithIgnoredKeys(resultUser, user1ExcpectedResult, [ 'guid', 'ObjectVersion' ], msg="Identity 1 result mismatch")
      if resultUser['UserID'] == userID2:
        id2Found = True
        self.assertJSONStringsEqualWithIgnoredKeys(resultUser, user2ExcpectedResult, [ 'guid', 'ObjectVersion' ], msg="Identity 2 result mismatch")
      
    self.assertTrue(id1Found, msg="Identity 1 not in response")
    self.assertTrue(id2Found, msg="Identity 2 not in response")
    
  def test_attemptToLoginWithoutProvidingCredentials(self):
    result = self.testClient.get(self.loginAPIPrefix + '/' + masterTenantName + '/authproviders')
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))
    masterAuthProviderGUID = resultJSON[ 'AuthProviders' ][0]['guid']
    
    loginJSON = {
      "authProviderGUID": masterAuthProviderGUID,
      "credentialJSON": { 
       }
    }
    result2 = self.testClient.post(
      self.loginAPIPrefix + '/' + masterTenantName + '/authproviders', 
      data=json.dumps(loginJSON), 
      content_type='application/json'
    )
    self.assertEqual(result2.status_code, 401)
    result2JSON = json.loads(result2.get_data(as_text=True))
    expectedResult = {'message': 'Invalid credentials provided'}
    self.assertJSONStringsEqualWithIgnoredKeys(result2JSON, expectedResult, [ ], msg="Wrong error message provided")

  def test_attemptToLoginProvidingValidUserWithNoPassword(self):
    result = self.testClient.get(self.loginAPIPrefix + '/' + masterTenantName + '/authproviders')
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))
    masterAuthProviderGUID = resultJSON[ 'AuthProviders' ][0]['guid']
    
    loginJSON = {
      "authProviderGUID": masterAuthProviderGUID,
      "credentialJSON": { 
        "username": env['APIAPP_DEFAULTHOMEADMINUSERNAME']
       }
    }
    result2 = self.testClient.post(self.loginAPIPrefix + '/' + masterTenantName + '/authproviders', data=json.dumps(loginJSON), content_type='application/json')
    self.assertEqual(result2.status_code, 401)
    result2JSON = json.loads(result2.get_data(as_text=True))
    expectedResult = {'message': 'Invalid credentials provided'}
    self.assertJSONStringsEqualWithIgnoredKeys(result2JSON, expectedResult, [ ], msg="Wrong error message provided")

