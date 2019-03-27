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
    obj.resetDataForTest()
    objVerIDToSaveAs = 123
    transactionContext = obj.startTransaction()
    with self.assertRaises(Exception) as context:
      savedVer = obj._saveJSONObject(appObj, "Test", "123", JSONString, objVerIDToSaveAs, transactionContext)
    self.checkGotRightException(context,WrongObjectVersionException)

  def test_saveFailsWithInvalidObjectVersionSecondSave(self):
    obj = ObjectStore_SQLAlchemy(ConfigDict)
    obj.resetDataForTest()
    objVerIDToSaveAs = 123
    transactionContext = obj.startTransaction()
    savedVer = obj._saveJSONObject(appObj, "Test", "123", JSONString, None, transactionContext)
    obj.commitTransaction(transactionContext)
    transactionContext = obj.startTransaction()
    with self.assertRaises(Exception) as context:
      savedVer = obj._saveJSONObject(appObj, "Test", "123", JSONString, objVerIDToSaveAs, transactionContext)
    obj.commitTransaction(transactionContext)
    self.checkGotRightException(context,WrongObjectVersionException)

  def test_saveObjectsInSingleTransaction(self):
    obj = ObjectStore_SQLAlchemy(ConfigDict)
    obj.resetDataForTest()
    lastSavedVer = None
    transactionContext = obj.startTransaction()
    for x in range(1,6): 
      savedVer = obj._saveJSONObject(appObj, "Test", "123", JSONString, lastSavedVer, transactionContext)
      self.assertEqual(savedVer, x)
      lastSavedVer = savedVer
    obj.commitTransaction(transactionContext)
    
    #Check object was saved correctly
    (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = obj._getObjectJSON(appObj, "Test", "123")
    self.assertJSONStringsEqualWithIgnoredKeys(JSONString, objectDICT, [  ], msg='Saved object dosen\'t match')
    
  def test_saveObjectsInMutipleTransactions(self):
    obj = ObjectStore_SQLAlchemy(ConfigDict)
    obj.resetDataForTest()
    lastSavedVer = None
    for x in range(1,6): 
      transactionContext = obj.startTransaction()
      savedVer = obj._saveJSONObject(appObj, "Test", "123", JSONString, lastSavedVer, transactionContext)
      obj.commitTransaction(transactionContext)
      self.assertEqual(savedVer, x)
      lastSavedVer = savedVer
    
    #Check object was saved correctly
    (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = obj._getObjectJSON(appObj, "Test", "123")
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
