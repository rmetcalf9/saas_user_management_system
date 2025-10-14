import TestHelperSuperClass
import unittest
import refreshTokenGeneration
import datetime
import pytz
from MockTenantObj import MockTenantObj

class MockGateway():
  def enrichJWTClaims(self, JWTDict):
    return JWTDict

class MockAppObj():
  APIAPP_JWTSECRET = 'ABC123xx'
  APIAPP_JWT_TOKEN_TIMEOUT = 100
  APIAPP_REFRESH_TOKEN_TIMEOUT = 200
  APIAPP_REFRESH_SESSION_TIMEOUT = 1000
  scheduler = None
  curDateTimeOverrideForTesting = None
  gateway = MockGateway()
  def setTestingDateTime(self, val):
    self.curDateTimeOverrideForTesting = val
  def getCurDateTime(self):
    if self.curDateTimeOverrideForTesting is None:
      return datetime.datetime.now(pytz.timezone("UTC"))
    return self.curDateTimeOverrideForTesting

class helpers(unittest.TestCase):
  def getRefreshTokenManager(self):
    return refreshTokenGeneration.RefreshTokenManager(self.mockAppObj)

  def stepTimeForward(self, stepSize = 51):
    newTime = self.mockAppObj.getCurDateTime() + datetime.timedelta(seconds=stepSize)
    self.mockAppObj.setTestingDateTime(newTime)
    return newTime

  testStartTime = None
  mockAppObj = None
  man = None
  def setUp(self):
    self.mockAppObj = MockAppObj()
    self.testStartTime = self.mockAppObj.getCurDateTime()

    self.man = self.getRefreshTokenManager()
    self.mockAppObj.setTestingDateTime(self.testStartTime)

  def testDown(self):
    self.mockAppObj = None

  def getFirstToken(self):
    tenantObj = MockTenantObj(self.mockAppObj)
    return self.man.generateRefreshTokenFirstTime(
      appObj=self.mockAppObj,
      userAuthInformationWithoutJWTorRefreshToken={},
      userDict={},
      key='x',
      personGUID='x',
      currentlyUsedAuthProviderGuid='',
      currentlyUsedAuthKey='aaa',
      tenantObj=tenantObj
    )

#@TestHelperSuperClass.wipd
class testExpiringDictClass(helpers):

  def test_canUseTokenOnce(self):
    firstTokenJSON = self.getFirstToken()
    self.assertEqual(firstTokenJSON["TokenExpiry"], (self.testStartTime + datetime.timedelta(seconds=int(self.mockAppObj.APIAPP_REFRESH_TOKEN_TIMEOUT))).isoformat())

    nd = self.man.getRefreshedAuthDetails(
      appObj=self.mockAppObj,
      existingToken=firstTokenJSON["token"],
      tenantObj=MockTenantObj(self.mockAppObj)
    )
    self.assertNotEqual(nd, None)

    nd = self.man.getRefreshedAuthDetails(
      appObj=self.mockAppObj,
      existingToken=firstTokenJSON["token"],
      tenantObj=MockTenantObj(self.mockAppObj)
    )
    self.assertEqual(nd, None, msg="Managed to use same token twice")

  def test_canUseRefreshTokenUntilSessionTimesOut(self):
    tokenRefreshSessionExpiryTime = self.testStartTime + datetime.timedelta(seconds=int(self.mockAppObj.APIAPP_REFRESH_SESSION_TIMEOUT))

    firstTokenJSON = self.getFirstToken()
    self.assertEqual(firstTokenJSON["TokenExpiry"], (self.testStartTime + datetime.timedelta(seconds=int(self.mockAppObj.APIAPP_REFRESH_TOKEN_TIMEOUT))).isoformat())

    nextTokenToUse = firstTokenJSON["token"]

    for x in range(0, 19):
      self.stepTimeForward()
      nextToken = self.man.getRefreshedAuthDetails(
        appObj=self.mockAppObj,
        existingToken=nextTokenToUse,
        tenantObj=MockTenantObj(self.mockAppObj)
      )
      self.assertNotEqual(nextToken, None, msg="Failed to reuse token on attempt " + str(x))
      nextTokenToUse = nextToken["refresh"]["token"]
      self.assertNotEqual(nextToken["jwtData"]["JWTToken"], None)

    self.stepTimeForward()
    nextToken = self.man.getRefreshedAuthDetails(
      appObj=self.mockAppObj,
      existingToken=nextTokenToUse,
      tenantObj=MockTenantObj(self.mockAppObj)
    )
    self.assertEqual(nextToken, None, msg="Was still able to use token after " + str(x) + " attempts")
    self.assertTrue(self.mockAppObj.getCurDateTime()>tokenRefreshSessionExpiryTime, msg="Token refresh failed before session expiry")

  def test_refreshTokenStillOKAfterTokenExpiryButBeforeRefreshExpiry(self):
    tokenExpiryTime = self.testStartTime + datetime.timedelta(seconds=int(self.mockAppObj.APIAPP_JWT_TOKEN_TIMEOUT))
    tokenRefreshExpiryTime = self.testStartTime + datetime.timedelta(seconds=int(self.mockAppObj.APIAPP_REFRESH_TOKEN_TIMEOUT))
    tokenRefreshSessionExpiryTime = self.testStartTime + datetime.timedelta(seconds=int(self.mockAppObj.APIAPP_REFRESH_SESSION_TIMEOUT))

    print("                   Test Start:", self.testStartTime.isoformat())
    print("              tokenExpiryTime:", tokenExpiryTime.isoformat())
    print("       tokenRefreshExpiryTime:", tokenRefreshExpiryTime.isoformat())
    print("tokenRefreshSessionExpiryTime:", tokenRefreshSessionExpiryTime.isoformat())

    def addSecond(time):
      return time + datetime.timedelta(seconds=int(1))

    firstTokenJSON = self.getFirstToken()
    self.mockAppObj.setTestingDateTime(addSecond(tokenExpiryTime))
    nextToken = self.man.getRefreshedAuthDetails(
      appObj=self.mockAppObj,
      existingToken=firstTokenJSON["token"],
      tenantObj=MockTenantObj(self.mockAppObj)
    )
    self.assertNotEqual(nextToken, None, msg="Session should have been valid")

  def test_refreshTokenNOTOKAfterRefreshTokenExpiryButBeforeRefreshSessionExpiry(self):
    tokenExpiryTime = self.testStartTime + datetime.timedelta(seconds=int(self.mockAppObj.APIAPP_JWT_TOKEN_TIMEOUT))
    tokenRefreshExpiryTime = self.testStartTime + datetime.timedelta(seconds=int(self.mockAppObj.APIAPP_REFRESH_TOKEN_TIMEOUT))
    tokenRefreshSessionExpiryTime = self.testStartTime + datetime.timedelta(seconds=int(self.mockAppObj.APIAPP_REFRESH_SESSION_TIMEOUT))

    print("                   Test Start:", self.testStartTime.isoformat())
    print("              tokenExpiryTime:", tokenExpiryTime.isoformat())
    print("       tokenRefreshExpiryTime:", tokenRefreshExpiryTime.isoformat())
    print("tokenRefreshSessionExpiryTime:", tokenRefreshSessionExpiryTime.isoformat())

    def addSecond(time):
      return time + datetime.timedelta(seconds=int(1))

    firstTokenJSON = self.getFirstToken()
    self.mockAppObj.setTestingDateTime(addSecond(tokenRefreshExpiryTime))
    nextToken = self.man.getRefreshedAuthDetails(
      appObj=self.mockAppObj,
      existingToken=firstTokenJSON["token"],
      tenantObj=MockTenantObj(self.mockAppObj)
    )
    self.assertEqual(nextToken, None, msg="Session should NOT have been valid")
