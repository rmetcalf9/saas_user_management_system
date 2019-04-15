from TestHelperSuperClass import testHelperAPIClient, env
#from apiSecurity import verifyAPIAccessUserLoginRequired
from appObj import appObj
from base64 import b64encode
from constants import masterTenantName, DefaultHasAccountRole, masterTenantDefaultSystemAdminRole

from constants import masterTenantName


class test_apiSecurity(testHelperAPIClient):
  pass
'''
  def test_returnsSuccessWithNoTokenFails(self):
    self.assertFalse(verifyAPIAccessUserLoginRequired(appObj, masterTenantName, None)[0])

  def test_returnsSuccessWithNoAccountFailes(self):
    UserID = 'abc123'
    userDict = {
      "UserID": UserID,
      "TenantRoles": {}
    }
    jwtToken = self.generateJWTToken(userDict)
    self.assertFalse(verifyAPIAccessUserLoginRequired(appObj.APIAPP_JWTSECRET, masterTenantName, jwtToken)[0])

  def test_returnsSuccessWithDefaultAccountPasses(self):
    UserID = 'abc123'
    userDict = {
      "UserID": UserID,
      "TenantRoles": { masterTenantName: [DefaultHasAccountRole]}
    }
    jwtToken = self.generateJWTToken(userDict)
    self.assertTrue(verifyAPIAccessUserLoginRequired(appObj.APIAPP_JWTSECRET, masterTenantName, jwtToken)[0])

  def test_needsMasterRoleButItIsNotThere(self):
    UserID = 'abc123'
    userDict = {
      "UserID": UserID,
      "TenantRoles": { masterTenantName: [DefaultHasAccountRole]}
    }
    jwtToken = self.generateJWTToken(userDict)
    self.assertFalse(verifyAPIAccessUserLoginRequired(appObj.APIAPP_JWTSECRET, masterTenantName, jwtToken, [masterTenantDefaultSystemAdminRole])[0])

  def test_needsMasterRoleAndHasIt(self):
    UserID = 'abc123'
    userDict = {
      "UserID": UserID,
      "TenantRoles": { masterTenantName: [DefaultHasAccountRole, masterTenantDefaultSystemAdminRole]}
    }
    jwtToken = self.generateJWTToken(userDict)
    self.assertTrue(verifyAPIAccessUserLoginRequired(appObj.APIAPP_JWTSECRET, masterTenantName, jwtToken, [masterTenantDefaultSystemAdminRole])[0])
'''
