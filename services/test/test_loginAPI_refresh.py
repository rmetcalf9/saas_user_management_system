from test_loginAPI import test_api as parent_test_api
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
    result2 = self.testClient.post('/api/login/' + masterTenantName + '/refresh', data=json.dumps({'token': refreshToken}), content_type='application/json')
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
    RefreshedLogin = self.testClient.post('/api/login/' + masterTenantName + '/refresh', data=json.dumps({'token': refreshToken}), content_type='application/json')
    self.assertEqual(RefreshedLogin.status_code, 200)
    refreshedLoginInfo = json.loads(RefreshedLogin.get_data(as_text=True))
    
    self.assertJSONStringsEqualWithIgnoredKeys(OrigLoginResult, refreshedLoginInfo, [ 'jwtData', 'refresh' ], msg='Data in origional auth details dosen\'t match new')
    
    # Check jwtData is as expected
    self.assertNotEqual(OrigLoginResult['jwtData']['JWTToken'],refreshedLoginInfo['jwtData']['JWTToken'],msg="New and old JWT tokens match")
    self.assertNotEqual(OrigLoginResult['jwtData']['TokenExpiry'],refreshedLoginInfo['jwtData']['TokenExpiry'],msg="New and old JWT tokens have the same expiry")
    
    # Check refresh is as expected
    self.assertNotEqual(OrigLoginResult['refresh']['token'],refreshedLoginInfo['refresh']['token'],msg="New and old refresh tokens match")
    self.assertNotEqual(OrigLoginResult['refresh']['TokenExpiry'],refreshedLoginInfo['refresh']['TokenExpiry'],msg="New and old refresh tokens have the same expiry")
    

  #TODO can't use same refresh token twice
  #TODO refresh token expires after refresh timout
  #TODO new refresh token extends expiry time sucessfully
  #TODO repeatadly getting refresh token until session timeout stops when session times out
