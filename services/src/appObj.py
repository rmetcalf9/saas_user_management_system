#appObj.py - This file contains the main application object
# to be constructed by app.py

#All times will be passed to callers in UTC
# it is up to the callers to convert into any desired user timezone

import pytz

from baseapp_for_restapi_backend_with_swagger import AppObjBaseClass as parAppObj, readFromEnviroment
from flask_restplus import fields
import time
import datetime
from serverInfoAPI import registerAPI as registerMainApi, resetData as resetMainApi
from loginAPI import registerAPI as registerLoginApi

from tenants import GetTenant, CreateMasterTenant
from constants import masterTenantName
from objectStores_base import createObjectStoreInstance
import bcrypt
from gatewayInterface import getGatewayInterface
import uuid
from constants import customExceptionClass
from refreshTokenGeneration import RefreshTokenManager

from apscheduler.schedulers.background import BackgroundScheduler

invalidConfigurationException = customExceptionClass('Invalid Configuration')

#Encryption operations make unit tests run slow
# if app is in testing more this dummy class
# skips the hashing stages (dosen't matter for unit tests)
class testOnlybcrypt():
  def gensalt():
    return b'$2b$12$lXti32XD6LkwYUnLw.1vh.'
  def hashpw(combo_password, salt):
    return combo_password

class appObjClass(parAppObj):
  curDateTimeOverrideForTesting = None
  serverStartTime = None
  version = None
  objectStore = None
  APIAPP_MASTERPASSWORDFORPASSHASH = None
  APIAPP_DEFAULTHOMEADMINUSERNAME = None
  APIAPP_DEFAULTHOMEADMINPASSWORD = None
  APIAPP_JWT_TOKEN_TIMEOUT = None
  APIAPP_REFRESH_TOKEN_TIMEOUT = None
  APIAPP_REFRESH_SESSION_TIMEOUT = None
  bcrypt = bcrypt
  gateway = None
  defaultUserGUID = None
  refreshTokenManager = None
  scheduler = None

  def init(self, env, serverStartTime, testingMode = False):
    self.scheduler = BackgroundScheduler()
    self.defaultUserGUID = str(uuid.uuid4())
    if testingMode:
      print("Warning testing mode active - proper encryption is not being used")
      self.bcrypt = testOnlybcrypt
      self.defaultUserGUID = 'FORCED-CONSTANT-TESTING-GUID'
    
    self.curDateTimeOverrideForTesting = None
    self.serverStartTime = serverStartTime
    self.version = readFromEnviroment(env, 'APIAPP_VERSION', None, None)
    super(appObjClass, self).init(env)
    resetMainApi(self)
    
    self.APIAPP_MASTERPASSWORDFORPASSHASH = readFromEnviroment(env, 'APIAPP_MASTERPASSWORDFORPASSHASH', None, None)
    self.APIAPP_DEFAULTHOMEADMINUSERNAME  = readFromEnviroment(env, 'APIAPP_DEFAULTHOMEADMINUSERNAME', 'Admin', None)
    self.APIAPP_DEFAULTHOMEADMINPASSWORD = readFromEnviroment(env, 'APIAPP_DEFAULTHOMEADMINPASSWORD', None, None) #no default must be read in
    self.APIAPP_JWT_TOKEN_TIMEOUT = int(readFromEnviroment(env, 'APIAPP_JWT_TOKEN_TIMEOUT', 60 * 5, None)) #default to five minutes
    self.APIAPP_REFRESH_TOKEN_TIMEOUT = int(readFromEnviroment(env, 'APIAPP_REFRESH_TOKEN_TIMEOUT', 60 * 10, None)) #default to ten minutes
    self.APIAPP_REFRESH_SESSION_TIMEOUT = int(readFromEnviroment(env, 'APIAPP_REFRESH_SESSION_TIMEOUT', 60 * 60 * 2, None)) #default to two hours
    
    if self.APIAPP_REFRESH_TOKEN_TIMEOUT < self.APIAPP_JWT_TOKEN_TIMEOUT:
      print("ERROR - APIAPP_REFRESH_TOKEN_TIMEOUT should never be less than APIAPP_JWT_TOKEN_TIMEOUT")
      raise invalidConfigurationException
    if self.APIAPP_REFRESH_SESSION_TIMEOUT < self.APIAPP_REFRESH_TOKEN_TIMEOUT:
      print("ERROR - APIAPP_REFRESH_SESSION_TIMEOUT should never be less than APIAPP_REFRESH_SESSION_TIMEOUT")
      raise invalidConfigurationException
    
    self.objectStore = createObjectStoreInstance(self)
    if GetTenant(self,masterTenantName) is None:
      CreateMasterTenant(self)
    
    self.gateway = getGatewayInterface(env)
    self.refreshTokenManager = RefreshTokenManager(self.APIAPP_REFRESH_TOKEN_TIMEOUT, self.APIAPP_REFRESH_SESSION_TIMEOUT)
    
    self.scheduler.start()

  def initOnce(self):
    super(appObjClass, self).initOnce()
    registerMainApi(self)
    registerLoginApi(self)
    self.flastRestPlusAPIObject.title = "SAAS User Management"
    self.flastRestPlusAPIObject.description = "API for saas_user_management_system\nhttps://github.com/rmetcalf9/saas_user_management_system"

  def setTestingDateTime(self, val):
    self.curDateTimeOverrideForTesting = val
  def getCurDateTime(self):
    if self.curDateTimeOverrideForTesting is None:
      return datetime.datetime.now(pytz.timezone("UTC"))
    return self.curDateTimeOverrideForTesting

  def stopThread(self):
    ##print("stopThread Called")
    self.scheduler.shutdown()

  #override exit gracefully to stop worker thread
  def exit_gracefully(self, signum, frame):
    self.stopThread()
    super(appObjClass, self).exit_gracefully(signum, frame)

appObj = appObjClass()
