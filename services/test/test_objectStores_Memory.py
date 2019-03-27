#from TestHelperSuperClass import testHelperAPIClient, env
from appObj import appObj
from TestHelperSuperClass import testHelperSuperClass
from objectStores_base import WrongObjectVersionException
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

ConfigDict = {}

class test_objectStoresMemory(testHelperSuperClass):
  def test_saveFailsWithInvalidObjectVersionFirstSave(self):
    obj = ObjectStore_Memory(ConfigDict)
    objVerIDToSaveAs = 123
    with self.assertRaises(Exception) as context:
      savedVer = obj._saveJSONObject(appObj, "Test", "123", JSONString, objVerIDToSaveAs, None)
    self.checkGotRightException(context,WrongObjectVersionException)

  def test_saveFailsWithInvalidObjectVersionSecondSave(self):
    obj = ObjectStore_Memory(ConfigDict)
    objVerIDToSaveAs = 123
    savedVer = obj._saveJSONObject(appObj, "Test", "123", JSONString, None, None)
    with self.assertRaises(Exception) as context:
      savedVer = obj._saveJSONObject(appObj, "Test", "123", JSONString, objVerIDToSaveAs, None)
    self.checkGotRightException(context,WrongObjectVersionException)

  def test_saveAndRetrieveObject(self):
    obj = ObjectStore_Memory(ConfigDict)
    lastSavedVer = None
    for x in range(1,6): 
      savedVer = obj._saveJSONObject(appObj, "Test", "123", JSONString, lastSavedVer, None)
      self.assertEqual(savedVer, x)
      lastSavedVer = savedVer
      
    #TODO Actual retrival Check

  def test_saveGetSaveObj(self):
    obj = ObjectStore_Memory(ConfigDict)
    lastSavedVer = None
    for x in range(1,6): 
      newJSONString = copy.deepcopy(JSONString)
      savedVer = obj._saveJSONObject(appObj, "Test", "123", newJSONString, lastSavedVer, None)
      newJSONString = copy.deepcopy( obj._getObjectJSON(appObj, "Test", "123"))
      
      self.assertEqual(savedVer, x)
      lastSavedVer = savedVer


  def test_creationDateSetCorrectly(self):
    obj = ObjectStore_Memory(ConfigDict)
    testDateTime = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testDateTime)
    savedVer = obj._saveJSONObject(appObj, "Test", "123", JSONString, None, None)
    objDict, ver, creationDateTime, lastUpdateDateTime = obj._getObjectJSON(appObj, "Test", "123")
    self.assertEqual(objDict, JSONString)
    self.assertEqual(ver, savedVer)
    self.assertEqual(creationDateTime, testDateTime)
    self.assertEqual(lastUpdateDateTime, testDateTime)
    
  def test_updateDateSetCorrectly(self):
    obj = ObjectStore_Memory(ConfigDict)
    testDateTime = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testDateTime)
    lastVersion = None
    incTime = testDateTime
    for x in range(1,6):
      appObj.setTestingDateTime(incTime)
      savedVer = obj._saveJSONObject(appObj, "Test", "123", JSONString, lastVersion, None)
      objDict, ver, creationDateTime, lastUpdateDateTime = obj._getObjectJSON(appObj, "Test", "123")
      self.assertEqual(objDict, JSONString)
      self.assertEqual(ver, savedVer)
      self.assertEqual(creationDateTime, testDateTime, msg="creation time not right")
      self.assertEqual(lastUpdateDateTime, incTime, msg="Update time not right")
      lastVersion = ver
      incTime = incTime + datetime.timedelta(seconds=60)
