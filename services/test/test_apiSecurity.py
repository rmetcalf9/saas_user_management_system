from TestHelperSuperClass import testHelperAPIClient, env
from apiSecurity import verifyAPIAccessUserLoginRequired
from jwtTokenGeneration import generateJWTToken
from appObj import appObj
from base64 import b64encode
from constants import masterTenantName, DefaultHasAccountRole, masterTenantDefaultSystemAdminRole

from constants import masterTenantName

class test_apiSecurity(testHelperAPIClient):

  def generateJWTToken(self, userDict):
    jwtSecretAndKey = {
      'secret': appObj.gateway.GetJWTTokenSecret(userDict['UserID']),
      'key': userDict['UserID']
    }
    personGUID = '123ABC'
    return generateJWTToken(appObj, userDict, jwtSecretAndKey, personGUID)['JWTToken']
    

  def test_returnsSuccessWithNoTokenFails(self):
    self.assertFalse(verifyAPIAccessUserLoginRequired(appObj, masterTenantName, None))

  def test_returnsSuccessWithNoAccountFailes(self):
    UserID = 'abc123'
    userDict = {
      "UserID": UserID,
      "TenantRoles": {}
    }
    jwtToken = self.generateJWTToken(userDict)
    self.assertFalse(verifyAPIAccessUserLoginRequired(appObj, masterTenantName, jwtToken))

  def test_returnsSuccessWithDefaultAccountPasses(self):
    UserID = 'abc123'
    userDict = {
      "UserID": UserID,
      "TenantRoles": { masterTenantName: [DefaultHasAccountRole]}
    }
    jwtToken = self.generateJWTToken(userDict)
    self.assertTrue(verifyAPIAccessUserLoginRequired(appObj, masterTenantName, jwtToken))

  def test_needsMasterRoleButItIsNotThere(self):
    UserID = 'abc123'
    userDict = {
      "UserID": UserID,
      "TenantRoles": { masterTenantName: [DefaultHasAccountRole]}
    }
    jwtToken = self.generateJWTToken(userDict)
    self.assertFalse(verifyAPIAccessUserLoginRequired(appObj, masterTenantName, jwtToken, [masterTenantDefaultSystemAdminRole]))

  def test_needsMasterRoleAndHasIt(self):
    UserID = 'abc123'
    userDict = {
      "UserID": UserID,
      "TenantRoles": { masterTenantName: [DefaultHasAccountRole, masterTenantDefaultSystemAdminRole]}
    }
    jwtToken = self.generateJWTToken(userDict)
    self.assertTrue(verifyAPIAccessUserLoginRequired(appObj, masterTenantName, jwtToken, [masterTenantDefaultSystemAdminRole]))
