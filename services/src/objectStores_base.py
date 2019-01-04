# Code to save JSON objects into a store.
#  Allows abstraction of particular store
#  This is the baseClass other stores inherit from


# Class that will store objects in memory only
class objectStoreMemoryClass():
  objectData = None
  def __init__(self):
    self.objectData = dict()
  def getDictForObjectType(self, objectType):
    if objectType not in self.objectData:
      self.objectData[objectType] = dict()
    return self.objectData[objectType]
  def saveJSONObject(self, appObj, objectType, objectKey, JSONString):
    self.getDictForObjectType(objectType)[objectKey] = JSONString
  def getObjectJSON(self, appObj, objectType, objectKey):
    objectTypeDict = self.getDictForObjectType(objectType)
    if objectKey in objectTypeDict:
      return objectTypeDict[objectKey]
    return None

    
#Based on applicaiton options create an instance of objectStore to be used
def createObjectStoreInstance(appObj):
  return objectStoreMemoryClass()

