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
JSONString2 = {
  'AA': "AA2",
  'BB': "BB2",
  "CC": {
    "CC.AA": "AA2",
    "CC.BB": "BB2",
    "CC.CC": "CC2"
  }
}

ConfigDict = {
  "Type":"SQLAlchemy",
  "connectionString":"mysql+pymysql://saas_user_man_user:saas_user_man_testing_password@127.0.0.1:10103/saas_user_man"
}
ConfigDict_withPrefix = {
  "Type":"SQLAlchemy",
  "connectionString":"mysql+pymysql://saas_user_man_user:saas_user_man_testing_password@127.0.0.1:10103/saas_user_man",
  "objectPrefix":"testPrefix"
}

class dummyException(Exception):
  pass

class test_objectStoresSQLAlchemy(testHelperSuperClass):

  def test_saveFailsWithInvalidObjectVersionFirstSave(self):
    obj = ObjectStore_SQLAlchemy(ConfigDict)
    obj.resetDataForTest(appObj)
    objVerIDToSaveAs = 123
    
    storeConnection = obj.getConnectionContext(appObj)
    def someFn(connectionContext):
      with self.assertRaises(Exception) as context:
        savedVer = storeConnection.saveJSONObject("Test", "123", JSONString, objVerIDToSaveAs)
      self.checkGotRightException(context,WrongObjectVersionException)
    storeConnection.executeInsideTransaction(someFn)

  def test_saveFailsWithInvalidObjectVersionSecondSave(self):
    obj = ObjectStore_SQLAlchemy(ConfigDict)
    obj.resetDataForTest(appObj)
    objVerIDToSaveAs = 123
    
    storeConnection = obj.getConnectionContext(appObj)
    def someFn(connectionContext):
      return storeConnection.saveJSONObject("Test", "123", JSONString, None)
    savedVer = storeConnection.executeInsideTransaction(someFn)
    
    def someFn2(connectionContext):
      gContext = None
      with self.assertRaises(Exception) as context:
        savedVer = storeConnection.saveJSONObject("Test", "123", JSONString, objVerIDToSaveAs)
      self.checkGotRightException(context,WrongObjectVersionException)
    storeConnection.executeInsideTransaction(someFn2)

  def test_singleSaveAndRetrieveCommittedTransaction(self):
    obj = ObjectStore_SQLAlchemy(ConfigDict)
    obj.resetDataForTest(appObj)
    storeConnection = obj.getConnectionContext(appObj)
    
    def someFn(connectionContext):
      savedVer = connectionContext.saveJSONObject("Test", "123", JSONString, None)
    savedVer = storeConnection.executeInsideTransaction(someFn)
    
    (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "123")
    self.assertJSONStringsEqualWithIgnoredKeys(objectDICT, JSONString, [  ], msg='Saved object dosen\'t match')
  
  def test_singleSaveAndRetrieveUncommittedTransaction(self):
    obj = ObjectStore_SQLAlchemy(ConfigDict)
    obj.resetDataForTest(appObj)
    storeConnection = obj.getConnectionContext(appObj)
    
    def someFn(connectionContext):
      savedVer = connectionContext.saveJSONObject("Test", "123", JSONString, None)
      (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "123")
      self.assertJSONStringsEqualWithIgnoredKeys(objectDICT, JSONString, [  ], msg='Saved object dosen\'t match')
    savedVer = storeConnection.executeInsideTransaction(someFn)
    
  def test_saveObjectsInSingleTransaction(self):
    obj = ObjectStore_SQLAlchemy(ConfigDict)
    obj.resetDataForTest(appObj)
    
    storeConnection = obj.getConnectionContext(appObj)
    
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
    
  def test_saveObjectsInMutipleTransactions(self):
    obj = ObjectStore_SQLAlchemy(ConfigDict)
    obj.resetDataForTest(appObj)
    lastSavedVer = None
    storeConnection = obj.getConnectionContext(appObj)
    for x in range(1,6): 
      def someFn(connectionContext):
        savedVer = connectionContext.saveJSONObject("Test", "123", JSONString, lastSavedVer)
        self.assertEqual(savedVer, x)
        return savedVer
      lastSavedVer = storeConnection.executeInsideTransaction(someFn)

    #Check object was saved correctly
    (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "123")
    self.assertJSONStringsEqualWithIgnoredKeys(objectDICT, JSONString, [  ], msg='Saved object dosen\'t match')

  def test_updateToDifferentJSONWorks(self):
    obj = ObjectStore_SQLAlchemy(ConfigDict)
    obj.resetDataForTest(appObj)
    lastSavedVer = None
    storeConnection = obj.getConnectionContext(appObj)
    def someFn(connectionContext):
      savedVer = connectionContext.saveJSONObject("Test", "123", JSONString, lastSavedVer)
      return savedVer
    lastSavedVer = storeConnection.executeInsideTransaction(someFn)
    def someFn2(connectionContext):
      savedVer = connectionContext.saveJSONObject("Test", "123", JSONString2, lastSavedVer)
      return savedVer
    lastSavedVer = storeConnection.executeInsideTransaction(someFn2)

    #Check object was saved correctly
    (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "123")
    self.assertJSONStringsEqualWithIgnoredKeys(objectDICT, JSONString2, [  ], msg='Saved object dosen\'t match')
    
 
  def test_creationDateSetCorrectly(self):
    obj = ObjectStore_SQLAlchemy(ConfigDict)
    obj.resetDataForTest(appObj)

    testDateTime = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testDateTime)
    
    storeConnection = obj.getConnectionContext(appObj)
    def someFn(connectionContext):
      savedVer = connectionContext.saveJSONObject("Test", "123", JSONString, None)
      objDict, ver, creationDateTime, lastUpdateDateTime = connectionContext.getObjectJSON("Test", "123")
      self.assertEqual(objDict, JSONString, msg="Saved object mismatch")
      self.assertEqual(ver, savedVer, msg="Saved ver mismatch")
      self.assertEqual(creationDateTime, testDateTime, msg="Creation date time wrong")
      self.assertEqual(lastUpdateDateTime, testDateTime, msg="Last update date time wrong")
    storeConnection.executeInsideTransaction(someFn)
 
    
  def test_updateDateSetCorrectly(self):
    obj = ObjectStore_SQLAlchemy(ConfigDict)
    obj.resetDataForTest(appObj)
    storeConnection = obj.getConnectionContext(appObj)
    def someFn(connectionContext):
      testDateTime = datetime.datetime.now(pytz.timezone("UTC"))
      appObj.setTestingDateTime(testDateTime)
      lastVersion = None
      incTime = testDateTime
      for x in range(1,6):
        appObj.setTestingDateTime(incTime)
        savedVer = connectionContext.saveJSONObject("Test", "123", JSONString, lastVersion)
        objDict, ver, creationDateTime, lastUpdateDateTime = connectionContext._getObjectJSON("Test", "123")
        self.assertEqual(objDict, JSONString)
        self.assertEqual(ver, savedVer)
        self.assertEqual(creationDateTime, testDateTime, msg="creation time not right")
        self.assertEqual(lastUpdateDateTime, incTime, msg="Update time not right")
        lastVersion = ver
        incTime = incTime + datetime.timedelta(seconds=60)
    storeConnection.executeInsideTransaction(someFn)

  #Different prefixes don't share data
  def test_differentPrefixesDontShareData(self):
    obj = ObjectStore_SQLAlchemy(ConfigDict)
    obj.resetDataForTest(appObj)
    obj2 = ObjectStore_SQLAlchemy(ConfigDict_withPrefix)
    obj2.resetDataForTest(appObj)
    storeConnection = obj.getConnectionContext(appObj)
    def someFn(connectionContext):
      for x in range(1,6):
        connectionContext.saveJSONObject("Test", "1_123" + str(x), JSONString, None)
    storeConnection.executeInsideTransaction(someFn)
    storeConnection2 = obj2.getConnectionContext(appObj)
    def someFn(connectionContext):
      for x in range(1,6):
        connectionContext.saveJSONObject("Test", "2_123" + str(x), JSONString, None)
    storeConnection2.executeInsideTransaction(someFn)

    for x in range(1,6):
      (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "1_123" + str(x))
      self.assertJSONStringsEqualWithIgnoredKeys(objectDICT, JSONString, [  ], msg='Saved object dosen\'t match')
      (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection2.getObjectJSON("Test", "1_123" + str(x))
      self.assertJSONStringsEqualWithIgnoredKeys(objectDICT, None, [  ], msg='Saved object dosen\'t match')
    
      (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "2_123" + str(x))
      self.assertJSONStringsEqualWithIgnoredKeys(objectDICT, None, [  ], msg='Saved object dosen\'t match')
      (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection2.getObjectJSON("Test", "2_123" + str(x))
      self.assertJSONStringsEqualWithIgnoredKeys(objectDICT, JSONString, [  ], msg='Saved object dosen\'t match')
    
  #Test rollback single transaction
  def test_rollbackTransactionIsSuccessful_InsertOnly(self):
    obj = ObjectStore_SQLAlchemy(ConfigDict)
    obj.resetDataForTest(appObj)
    storeConnection = obj.getConnectionContext(appObj)
    
    #Test creation of record rollback works
    # _no data to start with
    (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "1_123")
    self.assertJSONStringsEqualWithIgnoredKeys(objectDICT, None, [  ], msg='Object found before it was added')
  
    # insert data
    def someFn(connectionContext):
      connectionContext.saveJSONObject("Test", "1_123", JSONString, None)
      (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = connectionContext.getObjectJSON("Test", "1_123")
      self.assertJSONStringsEqualWithIgnoredKeys(objectDICT, JSONString, [  ], msg='object never added')
      raise dummyException("rollback")
    try:
      storeConnection.executeInsideTransaction(someFn)
    except dummyException:
      pass
    
    # _no data after rolledback insert start with
    (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "1_123")
    self.assertJSONStringsEqualWithIgnoredKeys(objectDICT, None, [  ], msg='Found but it should have rolled back')

  def test_rollbackTransactionIsSuccessful_UpdateOnly(self):
    obj = ObjectStore_SQLAlchemy(ConfigDict)
    obj.resetDataForTest(appObj)
    storeConnection = obj.getConnectionContext(appObj)
    
    # insert data
    def someFn(connectionContext):
      objVer = connectionContext.saveJSONObject("Test", "1_123", JSONString, None)
      (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = connectionContext.getObjectJSON("Test", "1_123")
      self.assertJSONStringsEqualWithIgnoredKeys(objectDICT, JSONString, [  ], msg='object not added')
      return objVer
    objVer = storeConnection.executeInsideTransaction(someFn)

    # _no data to start with
    (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "1_123")
    self.assertJSONStringsEqualWithIgnoredKeys(objectDICT, JSONString, [  ], msg='Object found before it was added')
  
    # update data
    def someFn(connectionContext):
      connectionContext.saveJSONObject("Test", "1_123", JSONString2, objVer)
      (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = connectionContext.getObjectJSON("Test", "1_123")
      self.assertJSONStringsEqualWithIgnoredKeys(objectDICT, JSONString2, [  ], msg='object not updated')
      raise dummyException("rollback")
    try:
      storeConnection.executeInsideTransaction(someFn)
    except dummyException:
      pass
    
    # Make sure data has revereted to origional value
    (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "1_123")
    self.assertJSONStringsEqualWithIgnoredKeys(objectDICT, JSONString, [  ], msg='Did not roll back to previous value')    
    
  # Make sure mutiple object keys are respected
  def test_differentKeys(self):
    obj = ObjectStore_SQLAlchemy(ConfigDict)
    obj.resetDataForTest(appObj)
    storeConnection = obj.getConnectionContext(appObj)
    def someFn(connectionContext):
      objKeyMap = {}
      for x in range(1,6):
        objKeyMap["1_123" + str(x)] = connectionContext.saveJSONObject("Test", "1_123" + str(x), JSONString, None)
      return objKeyMap
    objKeyMap = storeConnection.executeInsideTransaction(someFn)
    
    #update 3rd object to alternative data
    def someFn(connectionContext):
      connectionContext.saveJSONObject("Test", "1_123" + str(3), JSONString2, objKeyMap["1_123" + str(3)])
    storeConnection.executeInsideTransaction(someFn)

    for x in range(1,6):
      expRes = copy.deepcopy(JSONString)
      if x==3:
        expRes = copy.deepcopy(JSONString2)
      (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "1_123" + str(x))
      self.assertJSONStringsEqualWithIgnoredKeys(objectDICT, expRes, [  ], msg='Saved object dosen\'t match')

#TODO Decide if I want to refactor to use index rather primary key to remove limit on maximum key size
#      I probally do due to componed keys __TENANT__:__USER__:__ETC__