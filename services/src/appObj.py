#appObj.py - This file contains the main application object
# to be constructed by app.py

#All times will be passed to callers in UTC
# it is up to the callers to convert into any desired user timezone

import pytz

from baseapp_for_restapi_backend_with_swagger import AppObjBaseClass as parAppObj, readFromEnviroment, uniqueCommaSeperatedListClass
from flask_restx import fields
from flask import request
import time
import datetime
import ticketManager
import apiKeyManager

from APIlogin import registerAPI as registerLoginApi
from APIadmin import registerAPI as registerAdminApi
from APIcurrentAuth import registerAPI as registerCurAuthApi

from tenants import GetTenant, CreateMasterTenant, RegisterUser, onAppInit as tenantOnAppInit
from constants import masterTenantName, conDefaultUserGUID, conTestingDefaultPersonGUID, customExceptionClass
import constants
from object_store_abstraction import createObjectStoreInstance
from gatewayInterface import getGatewayInterface
import uuid
import json
from refreshTokenGeneration import RefreshTokenManager
from persons import GetPerson
from userPersonCommon import GetUser
from authProviders_base import resetStaticData as authProviders_resetStaticData

import autoConfigRunner as autoConfig

import logging
import sys

from apscheduler.schedulers.background import BackgroundScheduler

invalidConfigurationException = customExceptionClass('Invalid Configuration')

InvalidObjectStoreConfigInvalidJSONException = customExceptionClass('APIAPP_OBJECTSTORECONFIG value is not valid JSON')


class appObjClass(parAppObj):
  objectStore = None
  APIAPP_MASTERPASSWORDFORPASSHASH = None
  APIAPP_DEFAULTHOMEADMINUSERNAME = None
  APIAPP_DEFAULTHOMEADMINPASSWORD = None
  APIAPP_JWT_TOKEN_TIMEOUT = None
  APIAPP_REFRESH_TOKEN_TIMEOUT = None
  APIAPP_REFRESH_SESSION_TIMEOUT = None
  APIAPP_DEFAULTMASTERTENANTJWTCOLLECTIONALLOWEDORIGINFIELD = None
  APIAPP_OBJECTSTOREDETAILLOGGING = None
  APIAPP_AUTOCONFIG = None # will mainly be read from file by baseapp
  gateway = None
  defaultUserGUID = None
  testingDefaultPersonGUID = None
  refreshTokenManager = None
  scheduler = None
  RegisterUserFn = RegisterUser #First argument to registerUser is appObj
  TicketManager = None
  ApiKeyManager = None

  def setupLogging(self):
    root = logging.getLogger()
    #root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

  def init(self, env, serverStartTime, testingMode = False):
    ##self.setupLogging() Comment in when debugging

    self.TicketManager = ticketManager.ticketManagerClass(appObj=self)
    self.ApiKeyManager = apiKeyManager.apiKeyManagerClass(appObj=self)

    authProviders_resetStaticData()
    self.scheduler = BackgroundScheduler(timezone="UTC")
    self.defaultUserGUID = str(uuid.uuid4())
    if testingMode:
      self.defaultUserGUID = conDefaultUserGUID
      self.testingDefaultPersonGUID = conTestingDefaultPersonGUID

    super(appObjClass, self).init(env, serverStartTime, testingMode, serverinfoapiprefix='public/info')

    #This app always needs a JWT key
    if self.APIAPP_JWTSECRET is None:
      print("ERROR - APIAPP_JWTSECRET should always be set")
      raise invalidConfigurationException

    self.APIAPP_MASTERPASSWORDFORPASSHASH = readFromEnviroment(env, 'APIAPP_MASTERPASSWORDFORPASSHASH', None, None).strip()
    self.APIAPP_DEFAULTHOMEADMINUSERNAME  = readFromEnviroment(env, 'APIAPP_DEFAULTHOMEADMINUSERNAME', 'Admin', None).strip()
    self.APIAPP_DEFAULTHOMEADMINPASSWORD = readFromEnviroment(env, 'APIAPP_DEFAULTHOMEADMINPASSWORD', None, None).strip() #no default must be read in
    self.APIAPP_JWT_TOKEN_TIMEOUT = int(readFromEnviroment(env, 'APIAPP_JWT_TOKEN_TIMEOUT', 60 * 10, None)) #default to 10 minutes
    self.APIAPP_REFRESH_TOKEN_TIMEOUT = int(readFromEnviroment(env, 'APIAPP_REFRESH_TOKEN_TIMEOUT', 60 * 60 * 2, None)) #default to 2 hours
    self.APIAPP_REFRESH_SESSION_TIMEOUT = int(readFromEnviroment(env, 'APIAPP_REFRESH_SESSION_TIMEOUT', 60 * 60 * 12, None)) #default to 12 hours

    autoconfigraw = readFromEnviroment(
      env=env,
      envVarName='APIAPP_AUTOCONFIG',
      defaultValue='',
      acceptableValues=None,
      nullValueAllowed=False
    ).strip()
    if autoconfigraw == '':
      self.APIAPP_AUTOCONFIG = None
    else:
      try:
        self.APIAPP_AUTOCONFIG = json.loads(autoconfigraw)
      except:
        print("ERROR - APIAPP_AUTOCONFIG is not valid json")
        raise invalidConfigurationException

    if self.APIAPP_REFRESH_TOKEN_TIMEOUT < self.APIAPP_JWT_TOKEN_TIMEOUT:
      print("ERROR - APIAPP_REFRESH_TOKEN_TIMEOUT should never be less than APIAPP_JWT_TOKEN_TIMEOUT")
      raise invalidConfigurationException
    if self.APIAPP_REFRESH_SESSION_TIMEOUT < self.APIAPP_REFRESH_TOKEN_TIMEOUT:
      print("ERROR - APIAPP_REFRESH_SESSION_TIMEOUT should never be less than APIAPP_REFRESH_SESSION_TIMEOUT")
      raise invalidConfigurationException

    self.APIAPP_DEFAULTMASTERTENANTJWTCOLLECTIONALLOWEDORIGINFIELD = readFromEnviroment(env, 'APIAPP_DEFAULTMASTERTENANTJWTCOLLECTIONALLOWEDORIGINFIELD', 'http://localhost', None)

    # add to the baseapp default so allowed origns are in this list and extra vals
    self.accessControlAllowOriginObj = uniqueCommaSeperatedListClass(self.APIAPP_DEFAULTMASTERTENANTJWTCOLLECTIONALLOWEDORIGINFIELD + ", " + self.accessControlAllowOriginObj.toString())

    # print('uniqueCommaSeperatedListClass:', self.accessControlAllowOriginObj.toString())

    print('APIAPP_JWT_TOKEN_TIMEOUT:'+str(self.APIAPP_JWT_TOKEN_TIMEOUT) + ' seconds')
    print('APIAPP_REFRESH_TOKEN_TIMEOUT:'+str(self.APIAPP_REFRESH_TOKEN_TIMEOUT) + ' seconds')
    print('APIAPP_REFRESH_SESSION_TIMEOUT:'+str(self.APIAPP_REFRESH_SESSION_TIMEOUT) + ' seconds')

    objectStoreConfigJSON = readFromEnviroment(env, 'APIAPP_OBJECTSTORECONFIG', '{}', None)
    objectStoreConfigDict = None
    try:
      if objectStoreConfigJSON != '{}':
        objectStoreConfigDict = json.loads(objectStoreConfigJSON)
    except Exception as err:
      print(err) # for the repr
      print(str(err)) # for just the message
      print(err.args) # the arguments that the exception has been called with.
      raise(InvalidObjectStoreConfigInvalidJSONException)

    self.APIAPP_OBJECTSTOREDETAILLOGGING = readFromEnviroment(
      env=env,
      envVarName='APIAPP_OBJECTSTOREDETAILLOGGING',
      defaultValue='N',
      acceptableValues=['Y', 'N'],
      nullValueAllowed=True
    ).strip()
    if (self.APIAPP_OBJECTSTOREDETAILLOGGING=='Y'):
      print("APIAPP_OBJECTSTOREDETAILLOGGING set to Y - statement logging enabled")

    fns = {
      'getCurDateTime': self.getCurDateTime
    }
    self.objectStore = createObjectStoreInstance(
      objectStoreConfigDict,
      fns,
      detailLogging=(self.APIAPP_OBJECTSTOREDETAILLOGGING=='Y')
    )

    def dbChangingFn(storeConnection):
      if GetTenant(masterTenantName, storeConnection, appObj=self) is None:
        print("********No master tenant found - creating********")
        def someFn(connectionContext):
          CreateMasterTenant(self, testingMode, storeConnection)
        storeConnection.executeInsideTransaction(someFn)
    self.objectStore.executeInsideConnectionContext(dbChangingFn)

    self.gateway = getGatewayInterface(env, self)
    self.refreshTokenManager = RefreshTokenManager(self)

    self.scheduler.start()

    # Load origins from tenants
    def dbfn(storeConnection):
      for curTenant in storeConnection.getAllRowsForObjectType("tenants", None, None, ""):
        print("Loading allowed origins for " + curTenant[0]["Name"] + ":" + str(curTenant[0]["JWTCollectionAllowedOriginList"]))
        appObj.accessControlAllowOriginObj.addList(curTenant[0]["JWTCollectionAllowedOriginList"])

      ##return storeConnection.getPaginatedResult("tenants", paginatedParamValues, outputFN)
    self.objectStore.executeInsideConnectionContext(dbfn)


    if self.APIAPP_AUTOCONFIG != None:
      autoConfigRunner = autoConfig.AutoConfigRunner(self.APIAPP_AUTOCONFIG)
      def configRunnerFn(storeConnection):
        autoConfigRunner.run(self, storeConnection)
      self.objectStore.executeInsideTransaction(configRunnerFn)

    tenantOnAppInit(self)

  def initOnce(self):
    super(appObjClass, self).initOnce()
    registerLoginApi(self)
    registerAdminApi(self)
    registerCurAuthApi(self)
    self.flastRestPlusAPIObject.title = "SAAS User Management"
    self.flastRestPlusAPIObject.description = "API for saas_user_management_system\nhttps://github.com/rmetcalf9/saas_user_management_system"

  def stopThread(self):
    ##print("stopThread Called")
    self.scheduler.shutdown()

  #override exit gracefully to stop worker thread
  def exit_gracefully(self, signum, frame):
    self.stopThread()
    super(appObjClass, self).exit_gracefully(signum, frame)

  def apiSecurityCheck(self, request, tenant, requiredRoleList, headersToSearch, cookiesToSearch):
    decodedJWTToken = super(appObjClass, self).apiSecurityCheck(request, tenant, requiredRoleList, headersToSearch, cookiesToSearch)
    def someFn(connectionContext):
      return GetPerson(appObj, decodedJWTToken.getPersonID(), connectionContext), GetUser(appObj, decodedJWTToken.getUserID(), connectionContext)
    personObj, userObj = appObj.objectStore.executeInsideTransaction(someFn)
    if (personObj is None):
      raise constants.invalidPersonInToken('Invlaid person in token')
    if (userObj is None):
      raise constants.invalidUserInToken('Invlaid user in token')
    decodedJWTToken.personObj = personObj
    decodedJWTToken.userObj = userObj
    return decodedJWTToken

appObj = appObjClass()
