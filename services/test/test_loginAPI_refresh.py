from test_loginAPI import test_api as parent_test_api
from TestHelperSuperClass import env
from dateutil.parser import parse
import pytz
from appObj import appObj
from datetime import datetime, timedelta
from constants import masterTenantName
import json

class test_api(parent_test_api):
  def test_refreshTokenExpires(self):
    result2JSON = self.loginAsDefaultUser()
    refreshToken = result2JSON['refresh']['token']
    dt = parse(result2JSON['refresh']['TokenExpiry'])
    refreshExpiry = dt.astimezone(pytz.utc)

    appObj.setTestingDateTime(refreshExpiry + timedelta(seconds=int(1)))
    result2 = self.testClient.post(self.loginAPIPrefix + '/' + masterTenantName + '/refresh', data=json.dumps({'token': refreshToken}), content_type='application/json')
    self.assertEqual(result2.status_code, 401)
    
  def test_refreshTokenGivesNewJWTToken(self):
    curTime = datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(curTime)
    OrigLoginResult = self.loginAsDefaultUser()

    #Must go forward at least a second to make the new JWTToken be different
    appObj.setTestingDateTime(curTime + timedelta(seconds=int(1)))
    refreshToken = OrigLoginResult['refresh']['token']
    dt = parse(OrigLoginResult['refresh']['TokenExpiry'])
    refreshExpiry = dt.astimezone(pytz.utc)
    
    RefreshedLogin = self.testClient.post(self.loginAPIPrefix + '/' + masterTenantName + '/refresh', data=json.dumps({'token': refreshToken}), content_type='application/json')
    self.assertEqual(RefreshedLogin.status_code, 200)
    refreshedLoginInfo = json.loads(RefreshedLogin.get_data(as_text=True))
    
    self.assertFalse('other_date' in refreshedLoginInfo)
    
    self.assertJSONStringsEqualWithIgnoredKeys(OrigLoginResult, refreshedLoginInfo, [ 'jwtData', 'refresh' ], msg='Data in origional auth details dosen\'t match new')
    
    # Check jwtData is as expected
    self.assertNotEqual(OrigLoginResult['jwtData']['JWTToken'],refreshedLoginInfo['jwtData']['JWTToken'],msg="New and old JWT tokens match")
    self.assertNotEqual(OrigLoginResult['jwtData']['TokenExpiry'],refreshedLoginInfo['jwtData']['TokenExpiry'],msg="New and old JWT tokens have the same expiry")
    
    # Check refresh is as expected
    self.assertNotEqual(OrigLoginResult['refresh']['token'],refreshedLoginInfo['refresh']['token'],msg="New and old refresh tokens match")
    self.assertNotEqual(OrigLoginResult['refresh']['TokenExpiry'],refreshedLoginInfo['refresh']['TokenExpiry'],msg="New and old refresh tokens have the same expiry")

  def test_cantUseSameRefreshTokenTwice(self):
    OrigLoginResult = self.loginAsDefaultUser()
    RefreshedLogin = self.testClient.post(self.loginAPIPrefix + '/' + masterTenantName + '/refresh', data=json.dumps({'token': OrigLoginResult['refresh']['token']}), content_type='application/json')
    self.assertEqual(RefreshedLogin.status_code, 200)
    RefreshedLogin = self.testClient.post(self.loginAPIPrefix + '/' + masterTenantName + '/refresh', data=json.dumps({'token': OrigLoginResult['refresh']['token']}), content_type='application/json')
    self.assertEqual(RefreshedLogin.status_code, 401)

  def test_repeatadlyUseRefreshTokensUntilSessionTimesout(self):
    curTime = datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(curTime)
    OrigLoginResult = self.loginAsDefaultUser()
    timeRefreshSessionShouldEnd = curTime + timedelta(seconds=int(env['APIAPP_REFRESH_SESSION_TIMEOUT']))

    secondsToWaitBeforeTryingRefresh = int(env['APIAPP_REFRESH_TOKEN_TIMEOUT']) - 2
    refreshToken = OrigLoginResult['refresh']['token']
    
    times = 0
    running = True
    while running:
      times = times + 1
      self.assertTrue(times < 999, msg='Went through loop too many times')

      curTime = curTime + timedelta(seconds=secondsToWaitBeforeTryingRefresh)
      appObj.setTestingDateTime(curTime)
      
      RefreshedLogin = self.testClient.post(self.loginAPIPrefix + '/' + masterTenantName + '/refresh', data=json.dumps({'token': refreshToken}), content_type='application/json')
      if curTime > timeRefreshSessionShouldEnd:
        self.assertEqual(RefreshedLogin.status_code, 401, msg="Got a sucessful refresh beyond the time that the refresh session should have timed out")
        running = False
      else:
        self.assertEqual(RefreshedLogin.status_code, 200)
        refreshedLoginInfo = json.loads(RefreshedLogin.get_data(as_text=True))
        refreshToken = refreshedLoginInfo['refresh']['token']

    
  def test_newRefreshTokenHasExtendedExpiryTime(self):
    curTime = datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(curTime)
    OrigLoginResult = self.loginAsDefaultUser()
    
    dt = parse(OrigLoginResult['refresh']['TokenExpiry'])
    firstRefreshExpiry = dt.astimezone(pytz.utc)

    secondsToWaitBeforeTryingRefresh = int(env['APIAPP_REFRESH_TOKEN_TIMEOUT']) - 2
    curTime = curTime + timedelta(seconds=secondsToWaitBeforeTryingRefresh)
    appObj.setTestingDateTime(curTime)
    
    RefreshedLogin = self.testClient.post(self.loginAPIPrefix + '/' + masterTenantName + '/refresh', data=json.dumps({'token': OrigLoginResult['refresh']['token']}), content_type='application/json')
    refreshedLoginInfo = json.loads(RefreshedLogin.get_data(as_text=True))
    dt = parse(refreshedLoginInfo['refresh']['TokenExpiry'])
    secondRefreshExpiry = dt.astimezone(pytz.utc)
    
    secondsExtendedBy = (secondRefreshExpiry-firstRefreshExpiry).total_seconds()
    print(int(env['APIAPP_REFRESH_TOKEN_TIMEOUT']))
    print(secondsExtendedBy)
    
    self.assertTrue(secondsExtendedBy > 0, msg="New tokens refresh time isn't later than origional")
    self.assertTrue(secondsExtendedBy < int(env['APIAPP_REFRESH_TOKEN_TIMEOUT']), msg="Refresh time was extended by more than a signle time out")
