from datetime import datetime, timedelta
import pytz
from TestHelperSuperClass import testHelperAPIClient, env
from appObj import appObj
from constants import masterTenantName, jwtHeaderName
from test_adminAPI import test_api as parent_test_api

class test_adminAPIExpiry(parent_test_api):
  def test_expiredTokenReturns401(self):
    #create token respects appObj time
    # verify claim of token does not
    curTime = datetime.now(pytz.timezone("UTC"))
    timeToGenerateToken = curTime - timedelta(seconds=int(env['APIAPP_JWT_TOKEN_TIMEOUT'])) - timedelta(seconds=int(2))
    appObj.setTestingDateTime(timeToGenerateToken)
    
    expiredJwtToken = self.getNormalJWTToken()

    appObj.setTestingDateTime(curTime)
    
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/tenants', headers={ jwtHeaderName: expiredJwtToken})
    self.assertEqual(result.status_code, 401)
   

