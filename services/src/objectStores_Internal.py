# Code to save JSON objects into a store.
#  Allows abstraction of particular store
#  This is the baseClass other stores inherit from
StoringNoneObjectAfterUpdateOperationException = Exception('StoringNoneObjectAfterUpdateOperation')

# Class that will store objects in memory only
class objectStoreMemoryClass():
  objectData = None
  objectDataAlternativeKeys = None
  def __init__(self):
    self.objectData = dict()
    self.objectDataAlternativeKeys = dict()
  def _getDictForObjectType(self, objectType):
    if objectType not in self.objectData:
      #print("Creating dict for " + objectType)
      self.objectData[objectType] = dict()
    return self.objectData[objectType]

  def saveJSONObject(self, appObj, objectType, objectKey, JSONString):
    self._getDictForObjectType(objectType)[objectKey] = JSONString
  def removeJSONObject(self, appObj, objectType, objectKey):
    del self._getDictForObjectType(objectType)[objectKey]

  # Update the object in single operation. make transaction safe??
  def updateJSONObject(self, appObj, objectType, objectKey, updateFn):
    obj = self.getObjectJSON(appObj, objectType, objectKey)
    obj = updateFn(obj)
    if obj is None:
      raise StoringNoneObjectAfterUpdateOperationException
    self.saveJSONObject(appObj, objectType, objectKey, obj)
  
  def getObjectJSON(self, appObj, objectType, objectKey):
    objectTypeDict = self._getDictForObjectType(objectType)
    if objectKey in objectTypeDict:
      return objectTypeDict[objectKey]
    return None

#Based on applicaiton options create an instance of objectStore to be used
def createObjectStoreInstance(appObj):
  return objectStoreMemoryClass()

