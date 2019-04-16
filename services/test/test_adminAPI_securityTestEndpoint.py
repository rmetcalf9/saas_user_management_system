from datetime import datetime, timedelta
import pytz
from TestHelperSuperClass import testHelperAPIClient, env, tenantWithNoAuthProviders, sampleInternalAuthProv001_CREATE, internalUSerSufix, getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse
from appObj import appObj
from constants import masterTenantName, jwtHeaderName, objectVersionHeaderName, DefaultHasAccountRole, masterTenantDefaultSystemAdminRole, conDefaultUserGUID
import constants
from test_adminAPI import test_api as parent_test_api
import json
import copy

#Test security endpoint

def getTenantRoleDictFromTenantRoles(tenantRoles, tenantName):
  for x in tenantRoles:
    if x["TenantName"] == tenantName:
      return x
  a = {
    "TenantName": tenantName,
    "ThisTenantRoles": []
  }
  tenantRoles.append(a)
  return a

class test_security_endpoint(parent_test_api):
  def createSecurityUserUsingAdminAPI(self, authProviderDICT, username, password):
    hashedPassword = getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(username, password, authProviderDICT['saltForPasswordHashing'])
    
  
    newUserDICT = {
      "UserID": "securityUserID@TestUser",
      "known_as": "securityUserID",
      "mainTenant": masterTenantName
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/users', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newUserDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 201, msg="Create user failed - " + result.get_data(as_text=True))
    initialUserDICT = json.loads(result.get_data(as_text=True))
    
    #Add constants.SecurityEndpointAccessRole
    tenantRoleDict = getTenantRoleDictFromTenantRoles(initialUserDICT["TenantRoles"], masterTenantName)
    tenantRoleDict["ThisTenantRoles"].append(constants.SecurityEndpointAccessRole)
    
    result2 = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/users/' + initialUserDICT['UserID'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(initialUserDICT), 
      content_type='application/json'
    )
    self.assertEqual(result2.status_code, 200, msg="Add role failed - " + result.get_data(as_text=True))
    
    newUserDict = json.loads(result2.get_data(as_text=True))
    
    #Create a pseron
    result3 = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/persons', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps({}), 
      content_type='application/json'
    )
    self.assertEqual(result3.status_code, 201, msg="Add person failed - " + result.get_data(as_text=True))    
    newPersonDICT = json.loads(result3.get_data(as_text=True))
    
    #link user and person
    result4 = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/userpersonlinks/' + initialUserDICT['UserID'] + "/" + newPersonDICT['guid'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps({"UserID":initialUserDICT['UserID'],"personGUID":newPersonDICT['guid']}), 
      content_type='application/json'
    )
    self.assertEqual(result4.status_code, 201, msg="Add person link failed - " + result.get_data(as_text=True))    
    personLinkDICT = json.loads(result4.get_data(as_text=True))


    #Add internal auth so user can login
    postDict = {
      "personGUID":newPersonDICT['guid'],
      "tenantName":masterTenantName,
      "authProviderGUID":authProviderDICT['guid'],
      "credentialJSON":{"username":username,"password":hashedPassword}
    }
    result5 = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(postDict), 
      content_type='application/json'
    )
    self.assertEqual(result5.status_code, 201, msg="Add auth failed - " + result.get_data(as_text=True))    
    authDICT = json.loads(result5.get_data(as_text=True))
    
    return newUserDict
    
    
  def test_securityEndpointPasses(self):
    username='securityUserID'
    password='passssfds'
    authProviderDICT = self.getTenantInternalAuthProvDict(masterTenantName)
    securityUser = self.createSecurityUserUsingAdminAPI(authProviderDICT, username, password)
    
    loginResult = self.loginAsUser(masterTenantName, authProviderDICT, username, password)
    #print("loginResult:",loginResult)
    
    #User setup now access security endpoint
    result = self.testClient.get(
      self.adminAPIPrefix + '/' + masterTenantName + '/securityTestEndpoint', 
      headers={ jwtHeaderName: loginResult['jwtData']['JWTToken']},
    )
    self.assertEqual(result.status_code, 200, msg="Wrong response - " + result.get_data(as_text=True))
    res = json.loads(result.get_data(as_text=True))
    expectedRes = {'result': 'pass'}
    self.assertJSONStringsEqualWithIgnoredKeys(res,expectedRes, [], msg="Got incorrect response")

  def test_defaultUserCanAccessSecurityEndpoint(self):
    result = self.testClient.get(
      self.adminAPIPrefix + '/' + masterTenantName + '/securityTestEndpoint', 
      headers={ jwtHeaderName: self.getNormalJWTToken()},
    )
    self.assertEqual(result.status_code, 200, msg="Wrong response when testing admin access - " + result.get_data(as_text=True))
    res = json.loads(result.get_data(as_text=True))
    expectedRes = {'result': 'pass'}
    self.assertJSONStringsEqualWithIgnoredKeys(res,expectedRes, [], msg="Got incorrect response")
    

  