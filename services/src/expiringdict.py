from datetime import timedelta

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
