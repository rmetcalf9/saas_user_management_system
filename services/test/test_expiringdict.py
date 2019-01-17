import unittest
from datetime import datetime, timedelta
import pytz
from expiringdict import expiringdictClass

class turnAValueIntoAFunction():
  val = None
  def __init__(self, val):
    self.val = val
  def createdFunction(self):
    return self.val

class testExpiringDictClass(unittest.TestCase):
  def ensureKeyDoesntExist(self, expirintDictObj, time, key):
    foundKeyError = False
    try:
      val = expirintDictObj.getValue(time,key)
    except KeyError:
      foundKeyError = True
    self.assertTrue(foundKeyError, msg="Found key " + key + " which should not be present")

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
    self.ensureKeyDoesntExist(a, curTime,'key')

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

  def test_secondCleanUpThread(self):
    # class has a function designed to be run in a seperate thread to clean up
    # expired entries and prevent the dict growing eternaly. This test puts some 
    # data into the dict, goes forward in time, runs the clean up process
    # then goes back in time and makes sure the required keys are deleted

    durationToKeepItemInSeconds = 200
    keyWhichShouldBeDeleted = 'key_to_delete'
    keyWhichShouldNotBeDeleted = 'key_not_to_delete'
    
    curTime = datetime.now(pytz.timezone("UTC"))
    timeToCreateKeyWhichShouldBeDeleted = curTime
    timeToCreateKeyWhichShouldNotBeDeleted = curTime + timedelta(seconds=int(100))
    timeKeyForDeletionWillExpire = timeToCreateKeyWhichShouldBeDeleted +  timedelta(seconds=int(durationToKeepItemInSeconds))
    timeToRunCleanUpAt = timeKeyForDeletionWillExpire +  timedelta(seconds=int(10))

    timeToCheckForExistanceOfBothKeys = timeToCreateKeyWhichShouldNotBeDeleted + timedelta(seconds=int(10))

    objectUnderTest = expiringdictClass(durationToKeepItemInSeconds)

    #Create Keys
    objectUnderTest.addOrReplaceKey(timeToCreateKeyWhichShouldBeDeleted,keyWhichShouldBeDeleted,'val')
    objectUnderTest.addOrReplaceKey(timeToCreateKeyWhichShouldNotBeDeleted,keyWhichShouldNotBeDeleted,'val')

    #Make sure both exist (Will rasie an exception if they do not)
    res = objectUnderTest.getValue(timeToCheckForExistanceOfBothKeys,keyWhichShouldBeDeleted)
    res = objectUnderTest.getValue(timeToCheckForExistanceOfBothKeys,keyWhichShouldNotBeDeleted)

    #Run clean up process
    timeToRunCleanUpAtFN = turnAValueIntoAFunction(timeToRunCleanUpAt)
    objectUnderTest._cleanUpProcessWhichMayBeRunInSeperateThread(timeToRunCleanUpAtFN.createdFunction)

    #Next operation goes backwards in time - not a normal operaiton but it is a way we can
    # use to check what the clenaupprocess has done without triggering the automatic deletion
    # in the getValue procedure
    self.ensureKeyDoesntExist(objectUnderTest, timeToCheckForExistanceOfBothKeys,keyWhichShouldBeDeleted)
    res = objectUnderTest.getValue(timeToCheckForExistanceOfBothKeys,keyWhichShouldNotBeDeleted)

  def test_popValue(self):
    durationToKeepItemInSeconds = 20
    a = expiringdictClass(durationToKeepItemInSeconds)
    curTime = datetime.now(pytz.timezone("UTC"))
    a.addOrReplaceKey(curTime,'key','val')
    val = a.getValue(curTime,'key')
    self.assertEqual(val, 'val')
    val = a.popValue(curTime,'key')
    self.ensureKeyDoesntExist(a, curTime,'key')
    