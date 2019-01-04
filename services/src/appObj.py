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

from tenants import GetTenant, CreateMasterTenant
from constants import masterTenantName
from objectStores_base import createObjectStoreInstance

class appObjClass(parAppObj):
  curDateTimeOverrideForTesting = None
  serverStartTime = None
  version = None
  objectStore = None

  def init(self, env, serverStartTime, testingMode = False):
    self.curDateTimeOverrideForTesting = None
    self.serverStartTime = serverStartTime
    self.version = readFromEnviroment(env, 'APIAPP_VERSION', None, None)
    super(appObjClass, self).init(env)
    resetMainApi(self)
    self.objectStore = createObjectStoreInstance(self)
    if GetTenant(self,masterTenantName) is None:
      CreateMasterTenant(self)

  def initOnce(self):
    super(appObjClass, self).initOnce()
    registerMainApi(self)
    self.flastRestPlusAPIObject.title = "Reservation API"
    self.flastRestPlusAPIObject.description = "API for managing reservation system"

  def setTestingDateTime(self, val):
    self.curDateTimeOverrideForTesting = val
  def getCurDateTime(self):
    if self.curDateTimeOverrideForTesting is None:
      return datetime.datetime.now(pytz.timezone("UTC"))
    return self.curDateTimeOverrideForTesting


appObj = appObjClass()