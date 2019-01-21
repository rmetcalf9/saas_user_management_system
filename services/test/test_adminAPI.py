from TestHelperSuperClass import testHelperAPIClient, env
from constants import masterTenantName, jwtHeaderName, jwtCookieName, DefaultHasAccountRole, masterTenantDefaultSystemAdminRole

class test_api(testHelperAPIClient):
  def makeJWTTokenWithMasterTenantRoles(self, roles):
    UserID = 'abc123'
    userDict = {
      "UserID": UserID,
      "TenantRoles": { masterTenantName: roles}
    }
    return self.generateJWTToken(userDict)

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

  def test_jwtWorksAsHeader(self): 
    jwtToken = self.makeJWTTokenWithMasterTenantRoles([DefaultHasAccountRole, masterTenantDefaultSystemAdminRole])
    result = self.testClient.get('/api/admin/' + masterTenantName + '/tenants', headers={ jwtHeaderName: jwtToken})
    self.assertEqual(result.status_code, 200)

  def test_jwtWorksAsCookie(self): 
    jwtToken = self.makeJWTTokenWithMasterTenantRoles([DefaultHasAccountRole, masterTenantDefaultSystemAdminRole])
    self.testClient.set_cookie('localhost', jwtCookieName, jwtToken)
    result = self.testClient.get('/api/admin/' + masterTenantName + '/tenants')
    self.assertEqual(result.status_code, 200)

  def test_wrongTenantFails(self): 
    jwtToken = self.makeJWTTokenWithMasterTenantRoles([DefaultHasAccountRole, masterTenantDefaultSystemAdminRole])
    result = self.testClient.get('/api/admin/' + masterTenantName + 'xx/tenants', headers={ jwtHeaderName: jwtToken})
    self.assertEqual(result.status_code, 401)

