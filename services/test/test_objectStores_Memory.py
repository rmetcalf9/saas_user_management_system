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
    obj = ObjectStore_Memory(ConfigDict, appObj)
    objVerIDToSaveAs = 123
    with self.assertRaises(Exception) as context:
      storeConnection = obj.getConnectionContext()
      def someFn(connectionContext):
        savedVer = connectionContext.saveJSONObject("Test", "123", JSONString, objVerIDToSaveAs)
      storeConnection.executeInsideTransaction(someFn)
    self.checkGotRightException(context,WrongObjectVersionException)

  def test_saveFailsWithInvalidObjectVersionSecondSave(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    objVerIDToSaveAs = 123
    storeConnection = obj.getConnectionContext()
    def someFn(connectionContext):
      savedVer = connectionContext.saveJSONObject("Test", "123", JSONString, None)
      with self.assertRaises(Exception) as context:
        savedVer = connectionContext.saveJSONObject("Test", "123", JSONString, objVerIDToSaveAs)
      self.checkGotRightException(context,WrongObjectVersionException)

    storeConnection.executeInsideTransaction(someFn)
  
  def test_saveAndRetrieveObject(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    storeConnection = obj.getConnectionContext()
    
    def someFn(connectionContext):
      lastSavedVer = None
      for x in range(1,6): 
        savedVer = connectionContext.saveJSONObject("Test", "123", JSONString, lastSavedVer)
        self.assertEqual(savedVer, x)
        lastSavedVer = savedVer
    storeConnection.executeInsideTransaction(someFn)
      
    #Check object was saved correctly
    (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "123")
    self.assertJSONStringsEqualWithIgnoredKeys(JSONString, objectDICT, [  ], msg='Saved object dosen\'t match')
  
  def test_saveGetSaveObj(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    storeConnection = obj.getConnectionContext()

    def someFn(connectionContext):
      lastSavedVer = None
      for x in range(1,6): 
        newJSONString = copy.deepcopy(JSONString)
        savedVer = connectionContext.saveJSONObject("Test", "123", newJSONString, lastSavedVer)
        newJSONString = copy.deepcopy( connectionContext.getObjectJSON("Test", "123"))
        
        self.assertEqual(savedVer, x)
        lastSavedVer = savedVer
    storeConnection.executeInsideTransaction(someFn)

  def test_creationDateSetCorrectly(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    storeConnection = obj.getConnectionContext()
    testDateTime = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testDateTime)

    def someFn(connectionContext):
      return connectionContext.saveJSONObject("Test", "123", JSONString, None)
    savedVer = storeConnection.executeInsideTransaction(someFn)

    objDict, ver, creationDateTime, lastUpdateDateTime = storeConnection.getObjectJSON("Test", "123")
    self.assertEqual(objDict, JSONString)
    self.assertEqual(ver, savedVer)
    self.assertEqual(creationDateTime, testDateTime)
    self.assertEqual(lastUpdateDateTime, testDateTime)
    
  def test_updateDateSetCorrectly(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    storeConnection = obj.getConnectionContext()
    testDateTime = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testDateTime)
    lastVersion = None
    incTime = testDateTime
    for x in range(1,6):
      appObj.setTestingDateTime(incTime)
      
      def someFn(connectionContext):
        return connectionContext.saveJSONObject("Test", "123", JSONString, lastVersion)
      savedVer = storeConnection.executeInsideTransaction(someFn)
      
      objDict, ver, creationDateTime, lastUpdateDateTime = storeConnection.getObjectJSON("Test", "123")
      self.assertEqual(objDict, JSONString)
      self.assertEqual(ver, savedVer)
      self.assertEqual(creationDateTime, testDateTime, msg="creation time not right")
      self.assertEqual(lastUpdateDateTime, incTime, msg="Update time not right")
      lastVersion = ver
      incTime = incTime + datetime.timedelta(seconds=60)
