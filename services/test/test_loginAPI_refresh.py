from test_loginAPI import test_api as parent_test_api
from dateutil.parser import parse
import pytz
from appObj import appObj
from datetime import timedelta
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
    
    
  #TODO check refresh token gives us a new working JWT token
  #TODO can't use same refresh token twice
  #TODO refresh token expires after refresh timout
  #TODO new refresh token extends expiry time sucessfully
  #TODO repeatadly getting refresh token until session timeout stops when session times out
