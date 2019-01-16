import unittest
from datetime import datetime, timedelta
import pytz
from expiringdict import expiringdictClass

class testExpiringDictClass(unittest.TestCase):
  
  def test_storeAndRetrieve(self):
    durationToKeepItemInSeconds = 20
    a = expiringdictClass(durationToKeepItemInSeconds)
    curTime = datetime.now(pytz.timezone("UTC"))
    a.addOrReplaceKey(curTime,'key','val')
    val = a.getValue(curTime,'key')
    self.assertEqual(val, 'val')

  def test_retriveMissingValueGivesKeyError(self):
    durationToKeepItemInSeconds = 20
    a = expiringdictClass(durationToKeepItemInSeconds)
    curTime = datetime.now(pytz.timezone("UTC"))
    foundKeyError = False
    try:
      val = a.getValue(curTime,'key')
    except KeyError:
      foundKeyError = True
    self.assertTrue(foundKeyError, msg="ERROR key error not raised")

  def test_retriveExpiredValueGivesKeyError(self):
    durationToKeepItemInSeconds = 20
    a = expiringdictClass(durationToKeepItemInSeconds)
    curTime = datetime.now(pytz.timezone("UTC"))
    a.addOrReplaceKey(curTime,'key','val')
    endTime = datetime.now(pytz.timezone("UTC")) + timedelta(seconds=int(durationToKeepItemInSeconds)) + timedelta(seconds=int(2))
    foundKeyError = False
    try:
      val = a.getValue(endTime,'key')
    except KeyError:
      foundKeyError = True
    self.assertTrue(foundKeyError, msg="ERROR key error not raised")
