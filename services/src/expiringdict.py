from datetime import timedelta

# When using this class it may be nessecary to run the cleanupprocess in a background thread
#  this can be done by calling cleanUpProcessWhichMayBeRunInSeperateThread from https://apscheduler.readthedocs.io/en/v3.5.3/userguide.html

class expiringdictClass():
  durationToKeepItemInSeconds = None
  dataDict = None
  
  def __init__(self, durationToKeepItemInSeconds):
    self.durationToKeepItemInSeconds = durationToKeepItemInSeconds
    self.dataDict = dict()

  def addOrReplaceKey(self, curTime,key,val):
    expiryTime = curTime + timedelta(seconds=int(self.durationToKeepItemInSeconds))
    self.dataDict[key] = [val, expiryTime]
    
  def getValue(self, curTime,key):
    ite = self.dataDict[key]
    if ite[1] < curTime:
      del self.dataDict[key]
      raise KeyError
    return ite[0]

  def cleanUpProcessWhichMayBeRunInSeperateThread(self, curTime):
    keysThatHaveExpired = []
    for key in self.dataDict.keys():
      ite = self.dataDict[key]
      if ite[1] < curTime:
        keysThatHaveExpired.append(key)

    for key in keysThatHaveExpired:
      try:
        del self.dataDict[key]
      except KeyError:
        pass #key was deleted elsewhere maybe by attempted access