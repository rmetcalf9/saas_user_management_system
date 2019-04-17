#from TestHelperSuperClass import testHelperAPIClient, env
from TestHelperSuperClass import testHelperSuperClass, getObjectStoreExternalFns
from objectStores_base import WrongObjectVersionException, UnallowedMutationException, TriedToDeleteMissingObjectException, TryingToCreateExistingObjectException
from objectStores_Memory import ObjectStore_Memory
import copy
import datetime
#import json
import pytz
#from datetime import timedelta, datetime
#from dateutil.parser import parse

#from constants import masterTenantName, masterTenantDefaultDescription, masterTenantDefaultAuthProviderMenuText, masterTenantDefaultAuthProviderMenuIconLink

import test_objectStores_GenericTests as genericTests

ConfigDict = {}

class test_objectStoresMemory(testHelperSuperClass):
  def test_genericTests(self):
    def getObjFn(ConfigDict):
      return ObjectStore_Memory(ConfigDict, getObjectStoreExternalFns())
    genericTests.runAllGenericTests(self, getObjFn, ConfigDict)
  '''
  def test_saveFailsWithInvalidObjectVersionFirstSave(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    genericTests.saveFailsWithInvalidObjectVersionFirstSave(self, obj)

  def test_saveFailsWithInvalidObjectVersionSecondSave(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    genericTests.saveFailsWithInvalidObjectVersionSecondSave(self, obj)
  
  def test_singleSaveAndRetrieveCommittedTransaction(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    genericTests.singleSaveAndRetrieveCommittedTransaction(self, obj)
  
  def test_singleSaveAndRetrieveUncommittedTransaction(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    genericTests.singleSaveAndRetrieveUncommittedTransaction(self, obj)
    
  def test_saveObjectsInSingleTransaction(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    genericTests.saveObjectsInSingleTransaction(self, obj)
    
  def test_saveObjectsInMutipleTransactions(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    genericTests.saveObjectsInMutipleTransactions(self, obj)
    
  def test_creationDateSetCorrectly(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    genericTests.creationDateSetCorrectly(self, obj)
    
  def test_createExistingObjectFails(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    genericTests.createExistingObjectFails(self, obj)

  def test_supportsDifferentObjectTypes(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    genericTests.supportsDifferentObjectTypes(self, obj)
    
  def test_updateToDifferentJSONWorks(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    genericTests.updateToDifferentJSONWorks(self, obj)
 
  def test_updateDateSetCorrectly(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    genericTests.updateDateSetCorrectly(self, obj)
    
  def test_differentKeys(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    genericTests.differentKeys(self, obj)
    
  def test_updateUsingFunctionOutsideOfTransactionFails(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    genericTests.updateUsingFunctionOutsideOfTransactionFails(self, obj)

  def test_updateUsingFunction(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    genericTests.updateUsingFunction(self, obj)
    

  def test_removeMissingObject(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    genericTests.removeMissingObject(self, obj)

  def test_removeMissingObjectIgnoreMissing(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    genericTests.removeMissingObjectIgnoreMissing(self, obj)

  def test_removeObjectWithNoTransactionFails(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    genericTests.removeObjectWithNoTransactionFails(self, obj)

  def test_removeObject(self):
    obj = ObjectStore_Memory(ConfigDict, appObj)
    genericTests.removeObject(self, obj)
  '''
    
