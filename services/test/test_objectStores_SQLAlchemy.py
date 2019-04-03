#from TestHelperSuperClass import testHelperAPIClient, env
from appObj import appObj
from TestHelperSuperClass import testHelperSuperClass
from objectStores_base import WrongObjectVersionException, UnallowedMutationException, TriedToDeleteMissingObjectException, TryingToCreateExistingObjectException
from objectStores_SQLAlchemy import ObjectStore_SQLAlchemy
import copy
import datetime
#import json
import pytz
#from datetime import timedelta, datetime
#from dateutil.parser import parse

#from constants import masterTenantName, masterTenantDefaultDescription, masterTenantDefaultAuthProviderMenuText, masterTenantDefaultAuthProviderMenuIconLink

import test_objectStores_GenericTests as genericTests

import os
SKIPSQLALCHEMYTESTS=False
if ('SKIPSQLALCHEMYTESTS' in os.environ):
  if os.environ["SKIPSQLALCHEMYTESTS"]=="Y":
    SKIPSQLALCHEMYTESTS=True


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

#SQLAlchemt only test
def differentPrefixesDontShareData(testClass, objectStoreType, objectStoreType2):
  def dbfn(storeConnection):
    def dbfn2(storeConnection2):

      def someFn(connectionContext):
        for x in range(1,6):
          connectionContext.saveJSONObject("Test", "1_123" + str(x), JSONString, None)
      def someFn2(connectionContext2):
        for x in range(1,6):
          connectionContext2.saveJSONObject("Test", "2_123" + str(x), JSONString, None)

      storeConnection.executeInsideTransaction(someFn)
      storeConnection2.executeInsideTransaction(someFn2)

      for x in range(1,6):
        (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "1_123" + str(x))
        testClass.assertJSONStringsEqualWithIgnoredKeys(objectDICT, JSONString, [  ], msg='Saved object dosen\'t match')
        (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection2.getObjectJSON("Test", "1_123" + str(x))
        testClass.assertJSONStringsEqualWithIgnoredKeys(objectDICT, None, [  ], msg='Saved object dosen\'t match')
      
        (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection.getObjectJSON("Test", "2_123" + str(x))
        testClass.assertJSONStringsEqualWithIgnoredKeys(objectDICT, None, [  ], msg='Saved object dosen\'t match')
        (objectDICT, ObjectVersion, creationDate, lastUpdateDate) = storeConnection2.getObjectJSON("Test", "2_123" + str(x))
        testClass.assertJSONStringsEqualWithIgnoredKeys(objectDICT, JSONString, [  ], msg='Saved object dosen\'t match')
    objectStoreType2.executeInsideConnectionContext(dbfn2)
  objectStoreType.executeInsideConnectionContext(dbfn)

class test_objectStoresSQLAlchemy(testHelperSuperClass):
  def test_genericTests(self):
    if SKIPSQLALCHEMYTESTS:
      print("Skipping SQLAlchemyTests")
      return
    def getObjFn(ConfigDict):
      obj = ObjectStore_SQLAlchemy(ConfigDict, appObj)
      obj.resetDataForTest()
      return obj
    genericTests.runAllGenericTests(self, getObjFn, ConfigDict)

  #Different prefixes don't share data
  def test_differentPrefixesDontShareData(self):
    if SKIPSQLALCHEMYTESTS:
      print("Skipping SQLAlchemyTests")
      return
    obj = ObjectStore_SQLAlchemy(ConfigDict, appObj)
    obj.resetDataForTest()
    obj2 = ObjectStore_SQLAlchemy(ConfigDict_withPrefix, appObj)
    obj2.resetDataForTest()
    differentPrefixesDontShareData(self, obj, obj2)
    
  #Test rollback single transaction
  def test_rollbackTransactionIsSuccessful_InsertOnly(self):
    if SKIPSQLALCHEMYTESTS:
      print("Skipping SQLAlchemyTests")
      return
    obj = ObjectStore_SQLAlchemy(ConfigDict, appObj)
    obj.resetDataForTest()
    
    def dbfn(storeConnection):
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
      
    obj.executeInsideConnectionContext(dbfn)
  def test_rollbackTransactionIsSuccessful_UpdateOnly(self):
    if SKIPSQLALCHEMYTESTS:
      print("Skipping SQLAlchemyTests")
      return
    obj = ObjectStore_SQLAlchemy(ConfigDict, appObj)
    obj.resetDataForTest()
    
    def dbfn(storeConnection):
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

    obj.executeInsideConnectionContext(dbfn)
