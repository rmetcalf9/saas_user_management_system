#from TestHelperSuperClass import testHelperAPIClient, env
from appObj import appObj
from TestHelperSuperClass import testHelperSuperClass
from objectStores_base import WrongObjectVersionException
from objectStores_SQLAlchemy import ObjectStore_SQLAlchemy
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

ConfigDict = {
  "Type":"SQLAlchemy",
  "connectionString":"mysql+pymysql://saas_user_man_user:saas_user_man_testing_password@127.0.0.1:10103/saas_user_man"
}

class test_objectStoresSQLAlchemy(testHelperSuperClass):
  def test_saveFailsWithInvalidObjectVersionFirstSave(self):
    obj = ObjectStore_SQLAlchemy(ConfigDict)
    obj.resetDataForTest(appObj)
    objVerIDToSaveAs = 123
    
    storeConnection = obj.getConnectionContext(appObj)
    storeConnection.startTransaction()
    gContext = None
    try:
      with self.assertRaises(Exception) as context:
        savedVer = storeConnection._saveJSONObject("Test", "123", JSONString, objVerIDToSaveAs)
      gContext = context
      storeConnection.commitTransaction()
    except:
      storeConnection.rollbackTransaction()
      raise
    self.checkGotRightException(gContext,WrongObjectVersionException)


  def test_saveFailsWithInvalidObjectVersionSecondSave(self):
    obj = ObjectStore_SQLAlchemy(ConfigDict)
    obj.resetDataForTest(appObj)
    objVerIDToSaveAs = 123
    
    storeConnection = obj.getConnectionContext(appObj)
    storeConnection.startTransaction()
    try:
      savedVer = storeConnection._saveJSONObject("Test", "123", JSONString, None)
      storeConnection.commitTransaction()
    except:
      storeConnection.rollbackTransaction()
      raise    
    
    storeConnection.startTransaction()
    gContext = None
    try:
      with self.assertRaises(Exception) as context:
        savedVer = storeConnection._saveJSONObject("Test", "123", JSONString, objVerIDToSaveAs)
      storeConnection.commitTransaction()
      gContext = context
    except:
      storeConnection.rollbackTransaction()
      raise    
    self.checkGotRightException(gContext,WrongObjectVersionException)

  def test_saveObjectsInSingleTransaction(self):
    obj = ObjectStore_SQLAlchemy(ConfigDict)
    obj.resetDataForTest(appObj)
    lastSavedVer = None
    
    storeConnection = obj.getConnectionContext(appObj)
    storeConnection.startTransaction()
    try:
      for x in range(1,6): 
        savedVer = storeConnection._saveJSONObject("Test", "123", JSONString, lastSavedVer)
        self.assertEqual(savedVer, x)
        lastSavedVer = savedVer

      storeConnection.commitTransaction()
    except:
      storeConnection.rollbackTransaction()
      raise    
    
    #Check object was saved correctly
    (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection._getObjectJSON("Test", "123")
    self.assertJSONStringsEqualWithIgnoredKeys(JSONString, objectDICT, [  ], msg='Saved object dosen\'t match')
    
  def test_saveObjectsInMutipleTransactions(self):
    obj = ObjectStore_SQLAlchemy(ConfigDict)
    obj.resetDataForTest(appObj)
    lastSavedVer = None
    storeConnection = obj.getConnectionContext(appObj)
    for x in range(1,6): 
      storeConnection.startTransaction()
      try:
        savedVer = storeConnection._saveJSONObject("Test", "123", JSONString, lastSavedVer)
        storeConnection.commitTransaction()
        self.assertEqual(savedVer, x)
        lastSavedVer = savedVer
      except:
        storeConnection.rollbackTransaction()
        raise       
    
    #Check object was saved correctly
    (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection._getObjectJSON("Test", "123")
    self.assertJSONStringsEqualWithIgnoredKeys(JSONString, objectDICT, [  ], msg='Saved object dosen\'t match')

    
#  def test_creationDateSetCorrectly(self):
#    obj = ObjectStore_SQLAlchemy(ConfigDict)
#    testDateTime = datetime.datetime.now(pytz.timezone("UTC"))
#    appObj.setTestingDateTime(testDateTime)
#    savedVer = obj._saveJSONObject(appObj, "Test", "123", JSONString, None, None)
#    objDict, ver, creationDateTime, lastUpdateDateTime = obj._getObjectJSON(appObj, "Test", "123")
#    self.assertEqual(objDict, JSONString)
#    self.assertEqual(ver, savedVer)
#    self.assertEqual(creationDateTime, testDateTime)
#    self.assertEqual(lastUpdateDateTime, testDateTime)
    
#  def test_updateDateSetCorrectly(self):
#    obj = ObjectStore_SQLAlchemy(ConfigDict)
#    testDateTime = datetime.datetime.now(pytz.timezone("UTC"))
#    appObj.setTestingDateTime(testDateTime)
#    lastVersion = None
#    incTime = testDateTime
#    for x in range(1,6):
#      appObj.setTestingDateTime(incTime)
#      savedVer = obj._saveJSONObject(appObj, "Test", "123", JSONString, lastVersion, None)
#      objDict, ver, creationDateTime, lastUpdateDateTime = obj._getObjectJSON(appObj, "Test", "123")
#      self.assertEqual(objDict, JSONString)
#      self.assertEqual(ver, savedVer)
#      self.assertEqual(creationDateTime, testDateTime, msg="creation time not right")
#      self.assertEqual(lastUpdateDateTime, incTime, msg="Update time not right")
#      lastVersion = ver
#      incTime = incTime + datetime.timedelta(seconds=60)

#TODO Make sure we object keys are respected

#TODO Different prefixes don't share data

#TODO Test rollback single transaction

#TODO Test rollback mutiple transactions in same context


#TODO Test that all changes to data happen inside transactions
# this is important because unless executeInsideTransaction is used then developers might forget to execute commit
#  (Sometimes they think they are qurying when they are not)
#  one possible solution will be to always require a transaction even for queries
#   and completly dissalow manual calls of start/commit/rollback
