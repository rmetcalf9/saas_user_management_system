from TestHelperSuperClass import testHelperAPIClient, env
from constants import masterTenantName, jwtHeaderName, jwtCookieName, DefaultHasAccountRole, masterTenantDefaultSystemAdminRole
import json

class test_api(testHelperAPIClient):
  def makeJWTTokenWithMasterTenantRoles(self, roles):
    UserID = 'abc123'
    userDict = {
      "UserID": UserID,
      "TenantRoles": { masterTenantName: roles}
    }
    return self.generateJWTToken(userDict)


class test_securityTests(test_api):
  def test_noTokenSupplied(self):
    result = self.testClient.get('/api/admin/' + masterTenantName + '/tenants')
    self.assertEqual(result.status_code, 401)
  
  def test_jwtWithNoRoles(self): 
    jwtToken = self.makeJWTTokenWithMasterTenantRoles([])
    result = self.testClient.get('/api/admin/' + masterTenantName + '/tenants', headers={ jwtHeaderName: jwtToken})
    self.assertEqual(result.status_code, 401)

  def test_jwtWithOnlyAccountRole(self): 
    jwtToken = self.makeJWTTokenWithMasterTenantRoles([DefaultHasAccountRole])
    result = self.testClient.get('/api/admin/' + masterTenantName + '/tenants', headers={ jwtHeaderName: jwtToken})
    self.assertEqual(result.status_code, 401)

  def test_jwtWithOnlyAdminRole(self): 
    jwtToken = self.makeJWTTokenWithMasterTenantRoles([masterTenantDefaultSystemAdminRole])
    result = self.testClient.get('/api/admin/' + masterTenantName + '/tenants', headers={ jwtHeaderName: jwtToken})
    self.assertEqual(result.status_code, 401)

  def test_jwtWorksAsCookie(self): 
    jwtToken = self.makeJWTTokenWithMasterTenantRoles([DefaultHasAccountRole, masterTenantDefaultSystemAdminRole])
    self.testClient.set_cookie('localhost', jwtCookieName, jwtToken)
    result = self.testClient.get('/api/admin/' + masterTenantName + '/tenants')
    self.assertEqual(result.status_code, 200)

  def test_wrongTenantFails(self): 
    jwtToken = self.makeJWTTokenWithMasterTenantRoles([DefaultHasAccountRole, masterTenantDefaultSystemAdminRole])
    result = self.testClient.get('/api/admin/' + masterTenantName + 'xx/tenants', headers={ jwtHeaderName: jwtToken})
    self.assertEqual(result.status_code, 401)

  def test_jwtWorksAsHeader(self): 
    jwtToken = self.makeJWTTokenWithMasterTenantRoles([DefaultHasAccountRole, masterTenantDefaultSystemAdminRole])
    result = self.testClient.get('/api/admin/' + masterTenantName + '/tenants', headers={ jwtHeaderName: jwtToken})
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

class test_funcitonal(test_api):
  def test_jwtDefaultSingleTenant(self): 
    jwtToken = self.makeJWTTokenWithMasterTenantRoles([DefaultHasAccountRole, masterTenantDefaultSystemAdminRole])
    result = self.testClient.get('/api/admin/' + masterTenantName + '/tenants', headers={ jwtHeaderName: jwtToken})
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

    self.assertJSONStringsEqual(resultJSON['pagination'], {"offset": 0, "pagesize": 100, "total": 1})
    self.assertEqual(len(resultJSON["result"]),1,msg="Only 1 result should be returned")
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON["result"][0], {"AllowUserCreation": False, "AuthProviders": "ignored", "Description": "Master Tenant for User Management System", "Name": "usersystem"}, ['AuthProviders'])
    self.assertEqual(len(resultJSON["result"][0]['AuthProviders'].keys()),1,msg="Wrong number of auth providers")
    authProvGUID = None
    for a in resultJSON["result"][0]['AuthProviders'].keys():
      authProvGUID=a
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON["result"][0]['AuthProviders'][authProvGUID], {"AllowUserCreation": False, "ConfigJSON": {"userSufix": "@internalDataStore"}, "IconLink": None, "MenuText": "Website account login", "Type": "internal"}, ['guid', "saltForPasswordHashing"])
