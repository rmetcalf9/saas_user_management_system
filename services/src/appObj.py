#appObj.py - This file contains the main application object
# to be constructed by app.py

#All times will be passed to callers in UTC
# it is up to the callers to convert into any desired user timezone

import pytz

from baseapp_for_restapi_backend_with_swagger import AppObjBaseClass as parAppObj, readFromEnviroment
from flask_restplus import fields
import time
import datetime

from loginAPI import registerAPI as registerLoginApi
from adminAPI import registerAPI as registerAdminApi

from tenants import GetTenant, CreateMasterTenant
from constants import masterTenantName, conDefaultUserGUID, conTestingDefaultPersonGUID
from objectStores import createObjectStoreInstance
from gatewayInterface import getGatewayInterface
import uuid
from constants import customExceptionClass
from refreshTokenGeneration import RefreshTokenManager

from apscheduler.schedulers.background import BackgroundScheduler

invalidConfigurationException = customExceptionClass('Invalid Configuration')

class appObjClass(parAppObj):
  objectStore = None
  APIAPP_MASTERPASSWORDFORPASSHASH = None
  APIAPP_DEFAULTHOMEADMINUSERNAME = None
  APIAPP_DEFAULTHOMEADMINPASSWORD = None
  APIAPP_JWT_TOKEN_TIMEOUT = None
  APIAPP_REFRESH_TOKEN_TIMEOUT = None
  APIAPP_REFRESH_SESSION_TIMEOUT = None
  gateway = None
  defaultUserGUID = None
  testingDefaultPersonGUID = None
  refreshTokenManager = None
  scheduler = None

  def init(self, env, serverStartTime, testingMode = False):
    self.scheduler = BackgroundScheduler(timezone="UTC")
    self.defaultUserGUID = str(uuid.uuid4())
    if testingMode:
      self.defaultUserGUID = conDefaultUserGUID
      self.testingDefaultPersonGUID = conTestingDefaultPersonGUID
    
    super(appObjClass, self).init(env, serverStartTime, testingMode)
    
    self.APIAPP_MASTERPASSWORDFORPASSHASH = readFromEnviroment(env, 'APIAPP_MASTERPASSWORDFORPASSHASH', None, None).strip()
    self.APIAPP_DEFAULTHOMEADMINUSERNAME  = readFromEnviroment(env, 'APIAPP_DEFAULTHOMEADMINUSERNAME', 'Admin', None).strip()
    self.APIAPP_DEFAULTHOMEADMINPASSWORD = readFromEnviroment(env, 'APIAPP_DEFAULTHOMEADMINPASSWORD', None, None).strip() #no default must be read in
    self.APIAPP_JWT_TOKEN_TIMEOUT = int(readFromEnviroment(env, 'APIAPP_JWT_TOKEN_TIMEOUT', 60 * 5, None)) #default to five minutes
    self.APIAPP_REFRESH_TOKEN_TIMEOUT = int(readFromEnviroment(env, 'APIAPP_REFRESH_TOKEN_TIMEOUT', 60 * 10, None)) #default to ten minutes
    self.APIAPP_REFRESH_SESSION_TIMEOUT = int(readFromEnviroment(env, 'APIAPP_REFRESH_SESSION_TIMEOUT', 60 * 60 * 48, None)) #default to 48 hours
    
    if self.APIAPP_REFRESH_TOKEN_TIMEOUT < self.APIAPP_JWT_TOKEN_TIMEOUT:
      print("ERROR - APIAPP_REFRESH_TOKEN_TIMEOUT should never be less than APIAPP_JWT_TOKEN_TIMEOUT")
      raise invalidConfigurationException
    if self.APIAPP_REFRESH_SESSION_TIMEOUT < self.APIAPP_REFRESH_TOKEN_TIMEOUT:
      print("ERROR - APIAPP_REFRESH_SESSION_TIMEOUT should never be less than APIAPP_REFRESH_SESSION_TIMEOUT")
      raise invalidConfigurationException

    print('APIAPP_JWT_TOKEN_TIMEOUT:'+str(self.APIAPP_JWT_TOKEN_TIMEOUT) + ' seconds')
    print('APIAPP_REFRESH_TOKEN_TIMEOUT:'+str(self.APIAPP_REFRESH_TOKEN_TIMEOUT) + ' seconds')
    print('APIAPP_REFRESH_SESSION_TIMEOUT:'+str(self.APIAPP_REFRESH_SESSION_TIMEOUT) + ' seconds')

    self.objectStore = createObjectStoreInstance(self, env)
    def dbChangingFn(storeConnection):
      if GetTenant(masterTenantName, storeConnection, 'a','b','c') is None:
        print("********No master tenant found - creating********")
        def someFn(connectionContext):
          CreateMasterTenant(self, testingMode, storeConnection)
        storeConnection.executeInsideTransaction(someFn)
    self.objectStore.executeInsideConnectionContext(dbChangingFn)

    self.gateway = getGatewayInterface(env)
    self.refreshTokenManager = RefreshTokenManager(self)

    self.scheduler.start()

  def initOnce(self):
    super(appObjClass, self).initOnce()
    registerLoginApi(self)
    registerAdminApi(self)
    self.flastRestPlusAPIObject.title = "SAAS User Management"
    self.flastRestPlusAPIObject.description = "API for saas_user_management_system\nhttps://github.com/rmetcalf9/saas_user_management_system"

  def stopThread(self):
    ##print("stopThread Called")
    self.scheduler.shutdown()

  #override exit gracefully to stop worker thread
  def exit_gracefully(self, signum, frame):
    self.stopThread()
    super(appObjClass, self).exit_gracefully(signum, frame)

appObj = appObjClass()
