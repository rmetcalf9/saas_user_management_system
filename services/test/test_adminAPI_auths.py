from datetime import datetime, timedelta
import pytz
from TestHelperSuperClass import testHelperAPIClient, env, tenantWithNoAuthProviders, sampleInternalAuthProv001_CREATE, internalUSerSufix
from appObj import appObj
from constants import masterTenantName, jwtHeaderName, objectVersionHeaderName, DefaultHasAccountRole, masterTenantDefaultSystemAdminRole, uniqueKeyCombinator
from test_adminAPI import test_api as parent_test_api
import json
import copy
import base64

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

  def canWeLoginWithInternalAuth(self, authProviderGUID, username, password, tenantName):
    loginJSON = {
      "authProviderGUID": authProviderGUID,
      "credentialJSON": { 
        "username": username, 
        "password": password
       }
    }
    return self.testClient.post(self.loginAPIPrefix + '/' + tenantName + '/authproviders', data=json.dumps(loginJSON), content_type='application/json')
    
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
    loginTestResult = self.canWeLoginWithInternalAuth(newAuthDICT["authProviderGUID"], newAuthDICT["credentialJSON"]["username"], newAuthDICT["credentialJSON"]["password"], masterTenantName)
    self.assertEqual(loginTestResult.status_code, 200, msg='Could not log in - ' + result.get_data(as_text=True))  

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

    
  def test_createInternalAuthViaAdminAPIFailsWithDuplicateUsername(self):
    #creates auths for the default person
    
    newAuthDICT = self.getNewAuthDICT("testUsername")
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newAuthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 201, msg="Create auth failed - " + result.get_data(as_text=True))

    newAuthDICT = self.getNewAuthDICT("testUsername")
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newAuthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg="Create auth did not fail - " + result.get_data(as_text=True))

  def test_createInternalAuthViaAdminAPIFailsWithDuplicateUsernameCaseDiffers(self):
    #creates auths for the default person
    
    newAuthDICT = self.getNewAuthDICT("testUsername")
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newAuthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 201, msg="Create auth failed - " + result.get_data(as_text=True))

    newAuthDICT = self.getNewAuthDICT("testUsernaME") #Bad case is intentional
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newAuthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg="Create auth did not fail - " + result.get_data(as_text=True))

  def test_deleteInternalAuth(self):
    newAuthDICT = self.getNewAuthDICT()
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newAuthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 201, msg="Create auth failed - " + result.get_data(as_text=True))
    createAuthResultJSON = json.loads(result.get_data(as_text=True))

    #Check we can log in with created auth
    loginTestResult = self.canWeLoginWithInternalAuth(newAuthDICT["authProviderGUID"], newAuthDICT["credentialJSON"]["username"], newAuthDICT["credentialJSON"]["password"], masterTenantName)
    self.assertEqual(loginTestResult.status_code, 200, msg='Could not log in - ' + result.get_data(as_text=True))  

    base64EncodedKey = base64.b64encode(createAuthResultJSON['AuthUserKey'].encode('utf-8')).decode("utf-8") 
    deleteResult = self.testClient.delete(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths/' + base64EncodedKey,
      headers={ jwtHeaderName: self.getNormalJWTToken(), objectVersionHeaderName: None}
    )
    self.assertEqual(deleteResult.status_code, 200, msg="Delete Auth failed - " + deleteResult.get_data(as_text=True)) 
    deleteResultJSON = json.loads(deleteResult.get_data(as_text=True))
    
    expectedResult = {
      "AuthUserKey": createAuthResultJSON['AuthUserKey'],
      "authProviderGUID": newAuthDICT["authProviderGUID"],
      "personGUID": "FORCED-CONSTANT-TESTING-PERSON-GUID",
      "tenantName": masterTenantName
    }
    self.assertJSONStringsEqualWithIgnoredKeys(deleteResultJSON,expectedResult, [], msg="Delete Returned bad auth data")
    

    #Check we can no longer log in with created auth
    loginTestResult = self.canWeLoginWithInternalAuth(newAuthDICT["authProviderGUID"], newAuthDICT["credentialJSON"]["username"], newAuthDICT["credentialJSON"]["password"], masterTenantName)
    self.assertEqual(loginTestResult.status_code, 401, msg='Could log in - ' + result.get_data(as_text=True))  

  def test_deleteInternalAuthBadKey(self):
    newAuthDICT = self.getNewAuthDICT()
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newAuthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 201, msg="Create auth failed - " + result.get_data(as_text=True))
    createAuthResultJSON = json.loads(result.get_data(as_text=True))

    #Check we can log in with created auth
    loginTestResult = self.canWeLoginWithInternalAuth(newAuthDICT["authProviderGUID"], newAuthDICT["credentialJSON"]["username"], newAuthDICT["credentialJSON"]["password"], masterTenantName)
    self.assertEqual(loginTestResult.status_code, 200, msg='Could not log in - ' + result.get_data(as_text=True))  

    base64EncodedKey = base64.b64encode((createAuthResultJSON['AuthUserKey'] + 'abc').encode('utf-8')).decode("utf-8") 
    deleteResult = self.testClient.delete(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths/' + base64EncodedKey,
      headers={ jwtHeaderName: self.getNormalJWTToken(), objectVersionHeaderName: None}
    )
    self.assertEqual(deleteResult.status_code, 400, msg="Delete Auth failed - " + deleteResult.get_data(as_text=True)) 
    deleteResultJSON = json.loads(deleteResult.get_data(as_text=True))
    
  