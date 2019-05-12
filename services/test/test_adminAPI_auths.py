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

    #query the person and check it has two auths now
    getPersonresult = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/persons/' + createAuthResultJSON['personGUID'], headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(getPersonresult.status_code, 200)
    personResultJSON = json.loads(getPersonresult.get_data(as_text=True))
    self.assertEquals(len(personResultJSON['personAuths']),2,msg="Wrong number of auths in get Person result, was the auth created?")
    
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
    self.assertEqual(loginTestResult.status_code, 401, msg='Could log in after the auth was deleted - ' + result.get_data(as_text=True))
    
    #Check we can still query the person and the auth link there has been removed
    getPersonresult = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/persons/' + createAuthResultJSON['personGUID'], headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(getPersonresult.status_code, 200)
    personResultJSON = json.loads(getPersonresult.get_data(as_text=True))
    self.assertEquals(len(personResultJSON['personAuths']),1,msg="Wrong number of auths in get Person result")
    expectedResult = {
      'guid': 'FORCED-CONSTANT-TESTING-PERSON-GUID', 
      'associatedUsers': [{ #associatedUSers not checked but placed here for completeness
        'UserID': 'FORCED-CONSTANT-TESTING-GUID', 
        'known_as': 'AdminTestSet', 
        'TenantRoles': [{'TenantName': masterTenantName, 'ThisTenantRoles': [DefaultHasAccountRole, masterTenantDefaultSystemAdminRole]}], 
        'other_data': {'createdBy': 'init/CreateMasterTenant'}, 
        'associatedPersonGUIDs': ['FORCED-CONSTANT-TESTING-PERSON-GUID'], 
        'ObjectVersion': '3', 
        'creationDateTime': 'xx', 
        'lastUpdateDateTime': 'xx'
      }], 
      'personAuths': [{
        'AuthUserKey': "AdminTestSet" + internalUSerSufix + uniqueKeyCombinator + "internal", 
        'known_as': "AdminTestSet", 
        'AuthProviderType': 'internal', 
        'AuthProviderGUID': newAuthDICT["authProviderGUID"], 
        'tenantName': 'usersystem'
       }], 
      'ObjectVersion': '1', 
      'creationDateTime': 'xx', 
      'lastUpdateDateTime': 'xx'
    }
    self.assertJSONStringsEqualWithIgnoredKeys(personResultJSON,expectedResult, ['creationDateTime', 'lastUpdateDateTime', 'associatedUsers', 'personAuths'], msg="Ger person Returned bad auth data")
    self.assertJSONStringsEqualWithIgnoredKeys(personResultJSON['personAuths'],expectedResult['personAuths'], [], msg="Get person Returned bad list of perosnAuths")
     
    
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
    
  
