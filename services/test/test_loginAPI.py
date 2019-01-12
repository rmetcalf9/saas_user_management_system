from TestHelperSuperClass import testHelperAPIClient, env
import unittest
import json
from appObj import appObj
import pytz
import datetime
from dateutil.parser import parse

from constants import masterTenantName, masterTenantDefaultDescription, masterTenantDefaultAuthProviderMenuText, masterTenantDefaultAuthProviderMenuIconLink



invalidTenantName="invalidtenantname"

class test_api(testHelperAPIClient):

  def test_loginInvalidTenantFails(self):
    result = self.testClient.get('/api/login/' + invalidTenantName + '/authproviders')
    self.assertEqual(result.status_code, 400)
    resultJSON = json.loads(result.get_data(as_text=True))
    print(resultJSON)
    self.assertJSONStringsEqual(resultJSON, {"message": "Tenant not found"})

  def test_loginReturnsDefaultTenantAndAuthInfo(self):
    result = self.testClient.get('/api/login/' + masterTenantName + '/authproviders')
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
        "ConfigJSON": "{'userSufix': '@internalDataStore'}"
      }] 
    }
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON, expectedResult, [ 'AuthProviders' ])
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON[ 'AuthProviders' ][0], expectedResult[ 'AuthProviders' ][0], [ 'guid' ], msg="Master tenant auth provider wrong")

  def test_sucessfulLoginAsDefaultUser(self):
    result = self.testClient.get('/api/login/' + masterTenantName + '/authproviders')
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))
    masterAuthProviderGUID = resultJSON[ 'AuthProviders' ][0]['guid']
    
    loginJSON = {
      "authProviderGUID": masterAuthProviderGUID,
      "credentialJSON": { 
        "username": env['APIAPP_DEFAULTHOMEADMINUSERNAME'], 
        "password": env['APIAPP_DEFAULTHOMEADMINPASSWORD']
       }
    }
    result2 = self.testClient.post('/api/login/' + masterTenantName + '/authproviders', data=json.dumps(loginJSON), content_type='application/json')
    self.assertEqual(result2.status_code, 200)
    result2JSON = json.loads(result2.get_data(as_text=True))

    expectedResult = {
    }
    self.assertJSONStringsEqualWithIgnoredKeys(result2JSON, expectedResult, [ 'jwtData' ])

    expectedResult = {
    }
    self.assertJSONStringsEqualWithIgnoredKeys(result2JSON[ 'jwtData' ], expectedResult, [ 'JWTToken','TokenExpiry' ])
    
    jwtTokenDict = self.decodeToken(result2JSON[ 'jwtData' ]['JWTToken'])
    expectedTokenDict = {'UserID': 'FORCED-CONSTANT-TESTING-GUID', 'iss': '_CheckUserInitAndReturnJWTSecretAndKey_key', 'TenantRoles': {'usersystem': ['systemadmin', 'hasaccount']}, 'exp': 1547292391}
    self.assertJSONStringsEqualWithIgnoredKeys(jwtTokenDict, expectedTokenDict, [ 'exp' ])
    
    #Make sure passed expiry matches token expiry
    dt = parse(result2JSON['jwtData']['TokenExpiry'])
    dateTimeObjFromJSON = dt.astimezone(pytz.utc)

    dateTimeObjFromToken = datetime.datetime.fromtimestamp(jwtTokenDict['exp'],pytz.utc)
    time_diff = (dateTimeObjFromToken - dateTimeObjFromJSON).total_seconds()
    self.assertTrue(abs(time_diff) < 1,msg="More than 1 second difference between reported expiry time and actual expiry time in token")
    
    #Make sure expiry is in the future
    expectedExpiry = datetime.datetime.now(pytz.utc) + datetime.timedelta(seconds=int(env['APIAPP_JWT_TOKEN_TIMEOUT']))

    time_diff = (expectedExpiry - dateTimeObjFromJSON).total_seconds()
    self.assertTrue(abs(time_diff) < 1,msg="Token expiry not in correct range")

  def test_getMutipleIdentityResponseDefaultUser(self):
    userID1 = 'TestUser1'
    userID2 = 'TestUser2'
    InternalAuthUsername = 'ABC'
    res = self.createUserWithTwoIdentititesForOneUser(userID1, userID2, InternalAuthUsername)
    
    
    result = self.testClient.get('/api/login/' + masterTenantName + '/authproviders')
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
    result2 = self.testClient.post('/api/login/' + masterTenantName + '/authproviders', data=json.dumps(loginJSON), content_type='application/json')
    self.assertEqual(result2.status_code, 200)
    result2JSON = json.loads(result2.get_data(as_text=True))

    expectedResult = {
      'UserID': 'AdminTestSet', 
      'TenantRoles': {
        'usersystem': ['systemadmin', 'hasaccount']
      },
      'JWTToken': 'abc123'
    }
    print(result2JSON)
    
    #self.assertJSONStringsEqualWithIgnoredKeys(result2JSON, expectedResult, [ 'jwtToken' ])

    #TODO Check JWT token JSON is correct

    self.assertTrue(False)

