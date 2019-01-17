from datetime import timedelta

# This class uses https://pypi.org/project/APScheduler/ to launch a clean up thread
#  a valid apschedule (in memory) should be passed

class expiringdictClass():
  durationToKeepItemInSeconds = None
  dataDict = None
  
  def __init__(self, durationToKeepItemInSeconds, apSchedularInstance=None, curTimeFn=None):
    self.durationToKeepItemInSeconds = durationToKeepItemInSeconds
    self.dataDict = dict()
    if apSchedularInstance is not None:
      apSchedularInstance.add_job(self._cleanUpProcessWhichMayBeRunInSeperateThread, 'interval', minutes=10, id='my_job_id', args=[curTimeFn])

  def addOrReplaceKey(self, curTime,key,val):
    expiryTime = curTime + timedelta(seconds=int(self.durationToKeepItemInSeconds))
    self.dataDict[key] = [val, expiryTime]
    
  def getValue(self, curTime,key):
    ite = self.dataDict[key]
    if ite[1] < curTime:
      del self.dataDict[key]
      raise KeyError
    return ite[0]

  def _cleanUpProcessWhichMayBeRunInSeperateThread(self, curTimeFn):
    curTime = curTimeFn()
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