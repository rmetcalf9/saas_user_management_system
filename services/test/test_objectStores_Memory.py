#from TestHelperSuperClass import testHelperAPIClient, env
from appObj import appObj
from TestHelperSuperClass import testHelperSuperClass
from objectStores_base import WrongObjectVersionException, UnallowedMutationException, TriedToDeleteMissingObjectException, TryingToCreateExistingObjectException
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
JSONString2 = {
  'AA': "AA2",
  'BB': "BB2",
  "CC": {
    "CC.AA": "AA2",
    "CC.BB": "BB2",
    "CC.CC": "CC2"
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

  def test_updateUsingFunctionOutsideOfTransactionFails(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    storeConnection = obj.getConnectionContext()
    def someFn(connectionContext):
      return connectionContext.saveJSONObject("Test", "123", JSONString, None)
    savedVer = storeConnection.executeInsideTransaction(someFn)
    
    def updateFn(obj, connectionContext):
      self.assertJSONStringsEqualWithIgnoredKeys(JSONString, obj, [  ], msg='Saved object dosen\'t match')
      return JSONString2
    
    with self.assertRaises(Exception) as context:
      newVer = storeConnection.updateJSONObject("Test", "123", updateFn, savedVer)
    self.checkGotRightException(context,UnallowedMutationException)

  def test_updateUsingFunction(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    storeConnection = obj.getConnectionContext()
    def someFn(connectionContext):
      return connectionContext.saveJSONObject("Test", "123", JSONString, None)
    savedVer = storeConnection.executeInsideTransaction(someFn)
    
    def updateFn(obj, connectionContext):
      self.assertJSONStringsEqualWithIgnoredKeys(JSONString, obj, [  ], msg='Saved object dosen\'t match')
      return JSONString2

    def someFn(connectionContext):
      newVer = connectionContext.updateJSONObject("Test", "123", updateFn, savedVer)
    storeConnection.executeInsideTransaction(someFn)
    
    (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "123")
    self.assertJSONStringsEqualWithIgnoredKeys(JSONString2, objectDICT, [  ], msg='object was not updated')

  def test_removeMissingObject(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    storeConnection = obj.getConnectionContext()

    def someFn(connectionContext):
      newVer = connectionContext.removeJSONObject("Test", "123", 1, False)
    with self.assertRaises(Exception) as context:
      storeConnection.executeInsideTransaction(someFn)
    self.checkGotRightException(context,TriedToDeleteMissingObjectException)

  
  def test_removeMissingObjectIgnoreMissing(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    storeConnection = obj.getConnectionContext()

    def someFn(connectionContext):
      newVer = connectionContext.removeJSONObject("Test", "123", 1, True)
    storeConnection.executeInsideTransaction(someFn)

    (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "123")
    self.assertJSONStringsEqualWithIgnoredKeys(objectDICT, None, [  ], msg='object was not removed')

  def test_removeObjectWithNoTransactionFails(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    storeConnection = obj.getConnectionContext()
    def someFn(connectionContext):
      return connectionContext.saveJSONObject("Test", "123", JSONString, None)
    savedVer = storeConnection.executeInsideTransaction(someFn)

    (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "123")
    self.assertJSONStringsEqualWithIgnoredKeys(JSONString, objectDICT, [  ], msg='object was not added')

    with self.assertRaises(Exception) as context:
      newVer = storeConnection.removeJSONObject("Test", "123", savedVer, False)
    self.checkGotRightException(context,UnallowedMutationException)

  def test_removeObject(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    storeConnection = obj.getConnectionContext()
    def someFn(connectionContext):
      return connectionContext.saveJSONObject("Test", "123", JSONString, None)
    savedVer = storeConnection.executeInsideTransaction(someFn)

    (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "123")
    self.assertJSONStringsEqualWithIgnoredKeys(JSONString, objectDICT, [  ], msg='object was not added')

    def someFn(connectionContext):
      newVer = connectionContext.removeJSONObject("Test", "123", savedVer, False)
    storeConnection.executeInsideTransaction(someFn)

    (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "123")
    self.assertJSONStringsEqualWithIgnoredKeys(objectDICT, None, [  ], msg='object was not removed')

  def test_createExistingObjectFails(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    storeConnection = obj.getConnectionContext()
    def someFn(connectionContext):
      return connectionContext.saveJSONObject("Test", "123", JSONString, None)
    savedVer = storeConnection.executeInsideTransaction(someFn)

    (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "123")
    self.assertJSONStringsEqualWithIgnoredKeys(JSONString, objectDICT, [  ], msg='object was not added')


    with self.assertRaises(Exception) as context:
      savedVer = storeConnection.executeInsideTransaction(someFn)
    self.checkGotRightException(context,TryingToCreateExistingObjectException)
    
