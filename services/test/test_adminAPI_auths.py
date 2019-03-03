from datetime import datetime, timedelta
import pytz
from TestHelperSuperClass import testHelperAPIClient, env, tenantWithNoAuthProviders, sampleInternalAuthProv001_CREATE, internalUSerSufix
from appObj import appObj
from constants import masterTenantName, jwtHeaderName, objectVersionHeaderName, DefaultHasAccountRole, masterTenantDefaultSystemAdminRole, uniqueKeyCombinator
from test_adminAPI import test_api as parent_test_api
import json
import copy

#Test the filtering of the users request API


class test_adminAPIAuths(parent_test_api):
  def getNewAuthDICT(self, userName="testUsername"):
    masterTenant = self.getTenantDICT(masterTenantName)
    newAuthDICT = {
      "personGUID": "FORCED-CONSTANT-TESTING-PERSON-GUID",
      "tenantName": masterTenantName,
      "authProviderGUID": masterTenant["AuthProviders"][0]["guid"],
      "credentialJSON": { 
        "username": userName, 
        "password": self.getDefaultHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(masterTenant["AuthProviders"][0]["saltForPasswordHashing"])
      }
    }
    return copy.deepcopy(newAuthDICT)

  def test_createInternalAuth(self):
    #creates an auth for the default person
    
    newAuthDICT = self.getNewAuthDICT()
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newAuthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 201, msg="Create auth failed - " + result.get_data(as_text=True))
    resultJSON = json.loads(result.get_data(as_text=True))
    
    expectedResult = {
      "AuthUserKey": newAuthDICT["credentialJSON"]["username"] + internalUSerSufix + uniqueKeyCombinator + 'internal', 
      "authProviderGUID": newAuthDICT["authProviderGUID"], 
      "personGUID": "FORCED-CONSTANT-TESTING-PERSON-GUID", 
      "tenantName": masterTenantName
    }
    
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON, expectedResult, ["guid", "creationDateTime", "lastUpdateDateTime","associatedUsers"], msg='JSON of created Auth is not what was expected')
    
    #Check we can log in with created auth
    loginJSON = {
      "authProviderGUID": newAuthDICT["authProviderGUID"],
      "credentialJSON": { 
        "username": newAuthDICT["credentialJSON"]["username"], 
        "password": newAuthDICT["credentialJSON"]["password"]
       }
    }
    result2 = self.testClient.post(self.loginAPIPrefix + '/' + masterTenantName + '/authproviders', data=json.dumps(loginJSON), content_type='application/json')
    self.assertEqual(result2.status_code, 200)
    
    

  def test_createAuthInvalidTenantName(self):
    newAuthDICT = self.getNewAuthDICT()
    newAuthDICT['tenantName'] = "Invalid"

    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newAuthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg="Create auth did not fail - " + result.get_data(as_text=True))
    
  def test_createAuthInvalidPersonGUID(self):
    newAuthDICT = self.getNewAuthDICT()
    newAuthDICT['personGUID'] = "Invalid"

    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newAuthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg="Create auth did not fail - " + result.get_data(as_text=True))

  def test_createAuthInvalidauthProvGUID(self):
    newAuthDICT = self.getNewAuthDICT()
    newAuthDICT['authProviderGUID'] = "Invalid"

    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newAuthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg="Create auth did not fail - " + result.get_data(as_text=True))

  def test_createAuthInvalidauthConfig(self):
    newAuthDICT = self.getNewAuthDICT()
    newAuthDICT['credentialJSON'] = {"aa":"invalid"}

    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newAuthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg="Create auth did not fail - " + result.get_data(as_text=True))
