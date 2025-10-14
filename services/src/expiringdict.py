from datetime import timedelta

# This class uses https://pypi.org/project/APScheduler/ to launch a clean up thread
#  a valid apschedule (in memory) should be passed

class expiringdictClass():
  dataDict = None
  
  def __init__(self, apSchedularInstance=None, curTimeFn=None):
    self.dataDict = dict()
    if apSchedularInstance is not None:
      apSchedularInstance.add_job(self._cleanUpProcessWhichMayBeRunInSeperateThread, 'interval', minutes=10, id='my_job_id', args=[curTimeFn])

  def addOrReplaceKey(self, curTime, key, val, durationToKeepItemInSeconds):
    expiryTime = curTime + timedelta(seconds=int(durationToKeepItemInSeconds))
    self.dataDict[key] = [val, expiryTime]
    
  def getValue(self, curTime, key):
    ite = self.dataDict[key]
    if ite[1] < curTime:
      del self.dataDict[key]
      raise KeyError
    return ite[0]
    
  def popValue(self, curTime, key):
    val = self.getValue(curTime,key)
    del self.dataDict[key]
    return val

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
        pass #key may have been deleted elsewhere maybe by attempted access
      except Exception as e:
        #Also ignoring any other error. we will try again in the next run
        # but outputting to log
        print(e)
        print(str(e))
        print(e.args)
