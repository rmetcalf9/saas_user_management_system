#from TestHelperSuperClass import testHelperAPIClient, env
from appObj import appObj
import unittest
from objectStores_Memory import ObjectStore_Memory
import copy
#import json
#import pytz
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
    newJSONString = copy.deepcopy(JSONString)
    for x in range(1,6): 
      savedVer = obj._saveJSONObject(appObj, "Test", "123", newJSONString, lastSavedVer)
      newJSONString = copy.deepcopy( obj._getObjectJSON(appObj, "Test", "123"))
      
      self.assertEqual(savedVer, x)
      lastSavedVer = savedVer


#TODO Test creation date is set correctly

#TODO Test creation date is not updated when last update is
