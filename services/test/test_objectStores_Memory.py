#from TestHelperSuperClass import testHelperAPIClient, env
from appObj import appObj
import unittest
from objectStores_Memory import ObjectStore_Memory
import copy
import datetime
#import json
import pytz
#from datetime import timedelta, datetime
#from dateutil.parser import parse

#from constants import masterTenantName, masterTenantDefaultDescription, masterTenantDefaultAuthProviderMenuText, masterTenantDefaultAuthProviderMenuIconLink

JSONString = {
  'AA': "AA",
  'BB': "BB",
  "CC": {
    "CC.AA": "AA",
    "CC.BB": "BB",
    "CC.CC": "CC"
  }
}

class test_objectStoresMemory(unittest.TestCase):
  def test_saveAndRetrieveObject(self):
    obj = ObjectStore_Memory()
    lastSavedVer = None
    for x in range(1,6): 
      savedVer = obj._saveJSONObject(appObj, "Test", "123", JSONString, lastSavedVer)
      self.assertEqual(savedVer, x)
      lastSavedVer = savedVer

  def test_saveGetSaveObj(self):
    obj = ObjectStore_Memory()
    lastSavedVer = None
    for x in range(1,6): 
      newJSONString = copy.deepcopy(JSONString)
      savedVer = obj._saveJSONObject(appObj, "Test", "123", newJSONString, lastSavedVer)
      newJSONString = copy.deepcopy( obj._getObjectJSON(appObj, "Test", "123"))
      
      self.assertEqual(savedVer, x)
      lastSavedVer = savedVer


  def test_creationDateSetCorrectly(self):
    obj = ObjectStore_Memory()
    testDateTime = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testDateTime)
    savedVer = obj._saveJSONObject(appObj, "Test", "123", JSONString, None)
    objDict, ver, creationDateTime, lastUpdateDateTime = obj._getObjectJSON(appObj, "Test", "123")
    self.assertEqual(objDict, JSONString)
    self.assertEqual(ver, savedVer)
    self.assertEqual(creationDateTime, testDateTime)
    self.assertEqual(lastUpdateDateTime, testDateTime)
    
  def test_updateDateSetCorrectly(self):
    obj = ObjectStore_Memory()
    testDateTime = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testDateTime)
    lastVersion = None
    incTime = testDateTime
    for x in range(1,6):
      appObj.setTestingDateTime(incTime)
      savedVer = obj._saveJSONObject(appObj, "Test", "123", JSONString, lastVersion)
      objDict, ver, creationDateTime, lastUpdateDateTime = obj._getObjectJSON(appObj, "Test", "123")
      self.assertEqual(objDict, JSONString)
      self.assertEqual(ver, savedVer)
      self.assertEqual(creationDateTime, testDateTime, msg="creation time not right")
      self.assertEqual(lastUpdateDateTime, incTime, msg="Update time not right")
      lastVersion = ver
      incTime = incTime + datetime.timedelta(seconds=60)
