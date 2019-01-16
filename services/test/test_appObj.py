#tests for appObj
from TestHelperSuperClass import testHelperAPIClient, env
from appObj import appObj, appObjClass, invalidConfigurationException
from baseapp_for_restapi_backend_with_swagger import getInvalidEnvVarParamaterException
import pytz
import datetime
import json
import copy

class test_appObjClass(testHelperAPIClient):
#Actual tests below

  def test_CreateAppOBjInstance(self):
    pass

  def test_refeshTokenTimoutLessThanJWTTokenTimeoutGeneratesInvalidConfigException(self):
    envForTest = copy.deepcopy(env)
    envForTest['APIAPP_JWT_TOKEN_TIMEOUT'] ='60'
    envForTest['APIAPP_REFRESH_TOKEN_TIMEOUT'] = '30'
    with self.assertRaises(Exception) as context:
      appObj.init(envForTest, self.standardStartupTime, testingMode = True)
    self.checkGotRightException(context,invalidConfigurationException)

  def test_refreshSessionTimeoutLessThanRefeshTokenTimoutGeneratesInvalidConfigException(self):
    envForTest = copy.deepcopy(env)
    envForTest['APIAPP_REFRESH_TOKEN_TIMEOUT'] = '130'
    envForTest['APIAPP_REFRESH_SESSION_TIMEOUT'] ='115'
    with self.assertRaises(Exception) as context:
      appObj.init(envForTest, self.standardStartupTime, testingMode = True)
    self.checkGotRightException(context,invalidConfigurationException)

