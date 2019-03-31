#test_objectStores_GenericTests
# this file includes generic test base code for object stores
# so they don't need to be implemented in individual test classes.

from appObj import appObj
from objectStores_base import WrongObjectVersionException, UnallowedMutationException, TriedToDeleteMissingObjectException, TryingToCreateExistingObjectException
import datetime
import pytz
import copy

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


def runAllGenericTests(testClass, getObjFn, ConfigDict):
  curModuleName = globals()['__name__']
  for x in globals():
    if x.startswith("t_"):
      test_fn = globals()[x]
      obj = getObjFn(ConfigDict)
      test_fn(testClass, obj)

#*************************************
#   SaveJSONObject Tests
#*************************************


def t_saveFailsWithInvalidObjectVersionFirstSave(testClass, objectStoreType):
  objVerIDToSaveAs = 123
  
  storeConnection = objectStoreType.getConnectionContext()
  def someFn(connectionContext):
    with testClass.assertRaises(Exception) as context:
      savedVer = storeConnection.saveJSONObject("Test", "123", JSONString, objVerIDToSaveAs)
    testClass.checkGotRightException(context,WrongObjectVersionException)
  storeConnection.executeInsideTransaction(someFn)
  
def t_saveFailsWithInvalidObjectVersionSecondSave(testClass, objectStoreType):
  objVerIDToSaveAs = 123
  
  storeConnection = objectStoreType.getConnectionContext()
  def someFn(connectionContext):
    return storeConnection.saveJSONObject("Test", "123", JSONString, None)
  savedVer = storeConnection.executeInsideTransaction(someFn)
  
  def someFn2(connectionContext):
    gContext = None
    with testClass.assertRaises(Exception) as context:
      savedVer = storeConnection.saveJSONObject("Test", "123", JSONString, objVerIDToSaveAs)
    testClass.checkGotRightException(context,WrongObjectVersionException)
  storeConnection.executeInsideTransaction(someFn2)

def t_singleSaveAndRetrieveCommittedTransaction(testClass, objectStoreType):
  storeConnection = objectStoreType.getConnectionContext()
  
  def someFn(connectionContext):
    savedVer = connectionContext.saveJSONObject("Test", "123", JSONString, None)
  savedVer = storeConnection.executeInsideTransaction(someFn)
  
  (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "123")
  testClass.assertJSONStringsEqualWithIgnoredKeys(objectDICT, JSONString, [  ], msg='Saved object dosen\'t match')

def t_singleSaveAndRetrieveUncommittedTransaction(testClass, objectStoreType):
  storeConnection = objectStoreType.getConnectionContext()
  
  def someFn(connectionContext):
    savedVer = connectionContext.saveJSONObject("Test", "123", JSONString, None)
    (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "123")
    testClass.assertJSONStringsEqualWithIgnoredKeys(objectDICT, JSONString, [  ], msg='Saved object dosen\'t match')
  savedVer = storeConnection.executeInsideTransaction(someFn)
  
def t_saveObjectsInSingleTransaction(testClass, objectStoreType):
  storeConnection = objectStoreType.getConnectionContext()
  
  def someFn(connectionContext):
    lastSavedVer = None
    for x in range(1,6): 
      savedVer = connectionContext.saveJSONObject("Test", "123", JSONString, lastSavedVer)
      testClass.assertEqual(savedVer, x)
      lastSavedVer = savedVer
  storeConnection.executeInsideTransaction(someFn)
  
  #Check object was saved correctly
  (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "123")
  testClass.assertJSONStringsEqualWithIgnoredKeys(JSONString, objectDICT, [  ], msg='Saved object dosen\'t match')

def t_creationOfNewObjectNotAffectingOtherObjectTypeWithSameKey(testClass, objectStoreType):
  storeConnection = objectStoreType.getConnectionContext()
  
  def someFn(connectionContext):
    savedVer = connectionContext.saveJSONObject("Test1", "123", JSONString, None)
  savedVer = storeConnection.executeInsideTransaction(someFn)
  
  (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test1", "123")
  testClass.assertJSONStringsEqualWithIgnoredKeys(objectDICT, JSONString, [  ], msg='Saved object dosen\'t match')

  (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test2", "123")
  testClass.assertJSONStringsEqualWithIgnoredKeys(objectDICT, None, [  ], msg='creating object id 123 with type Test1 resulted in creation of object with id 123 and type test2')


def t_saveObjectsInMutipleTransactions(testClass, objectStoreType):
  lastSavedVer = None
  storeConnection = objectStoreType.getConnectionContext()
  for x in range(1,6): 
    def someFn(connectionContext):
      savedVer = connectionContext.saveJSONObject("Test", "123", JSONString, lastSavedVer)
      testClass.assertEqual(savedVer, x)
      return savedVer
    lastSavedVer = storeConnection.executeInsideTransaction(someFn)

  #Check object was saved correctly
  (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "123")
  testClass.assertJSONStringsEqualWithIgnoredKeys(objectDICT, JSONString, [  ], msg='Saved object dosen\'t match')

def t_creationDateSetCorrectly(testClass, objectStoreType):
  testDateTime = datetime.datetime.now(pytz.timezone("UTC"))
  appObj.setTestingDateTime(testDateTime)
  
  storeConnection = objectStoreType.getConnectionContext()
  def someFn(connectionContext):
    savedVer = connectionContext.saveJSONObject("Test", "123", JSONString, None)
    objDict, ver, creationDateTime, lastUpdateDateTime = connectionContext.getObjectJSON("Test", "123")
    testClass.assertEqual(objDict, JSONString, msg="Saved object mismatch")
    testClass.assertEqual(ver, savedVer, msg="Saved ver mismatch")
    testClass.assertEqual(creationDateTime, testDateTime, msg="Creation date time wrong")
    testClass.assertEqual(lastUpdateDateTime, testDateTime, msg="Last update date time wrong")
  storeConnection.executeInsideTransaction(someFn)

def t_createExistingObjectFails(testClass, objectStoreType):
  storeConnection = objectStoreType.getConnectionContext()
  def someFn(connectionContext):
    return connectionContext.saveJSONObject("Test", "123", JSONString, None)
  savedVer = storeConnection.executeInsideTransaction(someFn)

  (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "123")
  testClass.assertJSONStringsEqualWithIgnoredKeys(JSONString, objectDICT, [  ], msg='object was not added')

  with testClass.assertRaises(Exception) as context:
    savedVer = storeConnection.executeInsideTransaction(someFn)
  testClass.checkGotRightException(context,TryingToCreateExistingObjectException)

def t_supportsDifferentObjectTypes(testClass, objectStoreType):
  ##TODO Confirm this test
  storeConnection = objectStoreType.getConnectionContext()
  def someFn(connectionContext):
    a = connectionContext.saveJSONObject("TestType1", "123", JSONString, None)
    b = connectionContext.saveJSONObject("TestType2", "123", JSONString2, None)
  savedVer = storeConnection.executeInsideTransaction(someFn)

  (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("TestType1", "123")
  testClass.assertJSONStringsEqualWithIgnoredKeys(JSONString, objectDICT, [  ], msg='object was not added')
  
  (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("TestType2", "123")
  testClass.assertJSONStringsEqualWithIgnoredKeys(JSONString2, objectDICT, [  ], msg='object was not added')

#*************************************
#   UpdateJSONObject Tests
#*************************************

def t_updateToDifferentJSONWorks(testClass, objectStoreType):
  lastSavedVer = None
  storeConnection = objectStoreType.getConnectionContext()
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
  testClass.assertJSONStringsEqualWithIgnoredKeys(objectDICT, JSONString2, [  ], msg='Saved object dosen\'t match')

def t_updateDateSetCorrectly(testClass, objectStoreType):
  storeConnection = objectStoreType.getConnectionContext()
  def someFn(connectionContext):
    testDateTime = datetime.datetime.now(pytz.timezone("UTC"))
    appObj.setTestingDateTime(testDateTime)
    lastVersion = None
    incTime = testDateTime
    for x in range(1,6):
      appObj.setTestingDateTime(incTime)
      savedVer = connectionContext.saveJSONObject("Test", "123", JSONString, lastVersion)
      objDict, ver, creationDateTime, lastUpdateDateTime = connectionContext._getObjectJSON("Test", "123")
      testClass.assertEqual(objDict, JSONString)
      testClass.assertEqual(ver, savedVer)
      testClass.assertEqual(creationDateTime, testDateTime, msg="creation time not right")
      testClass.assertEqual(lastUpdateDateTime, incTime, msg="Update time not right")
      lastVersion = ver
      incTime = incTime + datetime.timedelta(seconds=60)
  storeConnection.executeInsideTransaction(someFn)

def t_differentKeys(testClass, objectStoreType):
  storeConnection = objectStoreType.getConnectionContext()
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
    testClass.assertJSONStringsEqualWithIgnoredKeys(objectDICT, expRes, [  ], msg='Saved object dosen\'t match')

def t_updateUsingFunctionOutsideOfTransactionFails(testClass, objectStoreType):
  storeConnection = objectStoreType.getConnectionContext()
  def someFn(connectionContext):
    return connectionContext.saveJSONObject("Test", "123", JSONString, None)
  savedVer = storeConnection.executeInsideTransaction(someFn)
  
  def updateFn(obj, connectionContext):
    testClass.assertJSONStringsEqualWithIgnoredKeys(JSONString, obj, [  ], msg='Saved object dosen\'t match')
    return JSONString2
  
  with testClass.assertRaises(Exception) as context:
    newVer = storeConnection.updateJSONObject("Test", "123", updateFn, savedVer)
  testClass.checkGotRightException(context,UnallowedMutationException)
    
def t_updateUsingFunction(testClass, objectStoreType):
  storeConnection = objectStoreType.getConnectionContext()
  def someFn(connectionContext):
    return connectionContext.saveJSONObject("Test", "123", JSONString, None)
  savedVer = storeConnection.executeInsideTransaction(someFn)
  
  def updateFn(obj, connectionContext):
    testClass.assertJSONStringsEqualWithIgnoredKeys(JSONString, obj, [  ], msg='Saved object dosen\'t match')
    return JSONString2

  def someFn(connectionContext):
    newVer = connectionContext.updateJSONObject("Test", "123", updateFn, savedVer)
  storeConnection.executeInsideTransaction(someFn)
  
  (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "123")
  testClass.assertJSONStringsEqualWithIgnoredKeys(JSONString2, objectDICT, [  ], msg='object was not updated')

#*************************************
#   RemoveJSONObject Tests
#*************************************


def t_removeMissingObject(testClass, objectStoreType):
  storeConnection = objectStoreType.getConnectionContext()

  def someFn(connectionContext):
    newVer = connectionContext.removeJSONObject("Test", "123", 1, False)
  with testClass.assertRaises(Exception) as context:
    storeConnection.executeInsideTransaction(someFn)
  testClass.checkGotRightException(context,TriedToDeleteMissingObjectException)

def t_removeMissingObjectIgnoreMissing(testClass, objectStoreType):
  storeConnection = objectStoreType.getConnectionContext()

  def someFn(connectionContext):
    newVer = connectionContext.removeJSONObject("Test", "123", 1, True)
  storeConnection.executeInsideTransaction(someFn)

  (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "123")
  testClass.assertJSONStringsEqualWithIgnoredKeys(objectDICT, None, [  ], msg='object was not removed')

def t_removeObjectWithNoTransactionFails(testClass, objectStoreType):
  storeConnection = objectStoreType.getConnectionContext()
  def someFn(connectionContext):
    return connectionContext.saveJSONObject("Test", "123", JSONString, None)
  savedVer = storeConnection.executeInsideTransaction(someFn)

  (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "123")
  testClass.assertJSONStringsEqualWithIgnoredKeys(JSONString, objectDICT, [  ], msg='object was not added')

  with testClass.assertRaises(Exception) as context:
    newVer = storeConnection.removeJSONObject("Test", "123", savedVer, False)
  testClass.checkGotRightException(context,UnallowedMutationException)

def t_removeObject(testClass, objectStoreType):
  storeConnection = objectStoreType.getConnectionContext()
  def someFn(connectionContext):
    return connectionContext.saveJSONObject("Test", "123", JSONString, None)
  savedVer = storeConnection.executeInsideTransaction(someFn)

  (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "123")
  testClass.assertJSONStringsEqualWithIgnoredKeys(JSONString, objectDICT, [  ], msg='object was not added')

  def someFn(connectionContext):
    newVer = connectionContext.removeJSONObject("Test", "123", savedVer, False)
  storeConnection.executeInsideTransaction(someFn)

  (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "123")
  testClass.assertJSONStringsEqualWithIgnoredKeys(objectDICT, None, [  ], msg='object was not removed')

def t_removeObjectOnlyRemovesKeyOfSameObjectType(testClass, objectStoreType):
  storeConnection = objectStoreType.getConnectionContext()
  #create 2 objects
  def someFn(connectionContext):
    savedVer1 = connectionContext.saveJSONObject("Test1", "123", JSONString, None)
    savedVer2 = connectionContext.saveJSONObject("Test2", "123", JSONString2, None)
    return (savedVer1, savedVer2)
  (savedVer1, savedVer2) = storeConnection.executeInsideTransaction(someFn)
  
  #check two different created objects exist (same key)
  (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test1", "123")
  testClass.assertJSONStringsEqualWithIgnoredKeys(objectDICT, JSONString, [  ], msg='object 1 not ok')
  (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test2", "123")
  testClass.assertJSONStringsEqualWithIgnoredKeys(objectDICT, JSONString2, [  ], msg='object 2 not ok')
  
  #Remove Object 1
  def someFn(connectionContext):
    newVer = connectionContext.removeJSONObject("Test1", "123", savedVer1, False)
  storeConnection.executeInsideTransaction(someFn)
  
  #Make sure object 1 is not there and object 2 is there
  (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test1", "123")
  testClass.assertJSONStringsEqualWithIgnoredKeys(objectDICT, None, [  ], msg='object was not removed')
  (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test2", "123")
  testClass.assertJSONStringsEqualWithIgnoredKeys(objectDICT, JSONString2, [  ], msg='object2 should not have been removed')
  
  
