from TestHelperSuperClass import testHelperAPIClientUsingSQLAlchemy, env
from constants import masterTenantName, masterTenantDefaultSystemAdminRole, DefaultHasAccountRole
import constants
import json
from dateutil.parser import parse
import pytz
from datetime import timedelta, datetime

import os
SKIPSQLALCHEMYTESTS=False
if ('SKIPSQLALCHEMYTESTS' in os.environ):
  if os.environ["SKIPSQLALCHEMYTESTS"]=="Y":
    SKIPSQLALCHEMYTESTS=True


class test_SQLAlchemyExtraTests(testHelperAPIClientUsingSQLAlchemy):
  def test_sucessfulLoginAsDefaultUser(self):
    if SKIPSQLALCHEMYTESTS:
      print("Skipping SQLAlchemyTests")
      return

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
      "ThisTenantRoles": [masterTenantDefaultSystemAdminRole, DefaultHasAccountRole, constants.SecurityEndpointAccessRole],
      "known_as": env['APIAPP_DEFAULTHOMEADMINUSERNAME'],
      "currentlyUsedAuthKey": "AdminTestSet@internalDataStore_`@\\/'internal"
    }
    self.assertJSONStringsEqualWithIgnoredKeys(result2JSON, expectedResult, [ 'jwtData', 'authedPersonGuid', 'refresh', 'currentlyUsedAuthProviderGuid' ])

    expectedResult = {
    }
    self.assertJSONStringsEqualWithIgnoredKeys(result2JSON[ 'jwtData' ], expectedResult, [ 'JWTToken','TokenExpiry' ])
    
    jwtTokenDict = self.decodeToken(result2JSON[ 'jwtData' ]['JWTToken'])
    expectedTokenDict = {
      'UserID': 'FORCED-CONSTANT-TESTING-GUID', 
      'iss': 'FORCED-CONSTANT-TESTING-GUID', 
      'TenantRoles': {
        'usersystem': [masterTenantDefaultSystemAdminRole, DefaultHasAccountRole, constants.SecurityEndpointAccessRole]
      }, 
      'exp': 1547292391,
      'authedPersonGuid': 'Ignore',
      "known_as": env['APIAPP_DEFAULTHOMEADMINUSERNAME'],
      "other_data": {
        "createdBy": "init/CreateMasterTenant"
      },
      "currentlyUsedAuthKey": "AdminTestSet@internalDataStore_`@\\/'internal"
    }
    self.assertJSONStringsEqualWithIgnoredKeys(jwtTokenDict, expectedTokenDict, [ 'exp', 'authedPersonGuid', 'associatedPersons', 'currentlyUsedAuthProviderGuid' ])
    
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
