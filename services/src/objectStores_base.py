# Code to save JSON objects into a store.
#  Allows abstraction of particular store
#  This is the baseClass other stores inherit from


# Class that will store objects in memory only
class objectStoreMemoryClass():
  objectData = dict()
  def saveJSONObject(self, appObj, objectKey, JSONString):
    self.objectData[objectKey] = JSONString
  def getObjectJSON(self, appObj, objectKey):
    if objectKey in self.objectData:
      return self.objectData[objectKey]
    return None

    
#Based on applicaiton options create an instance of objectStore to be used
def createObjectStoreInstance(appObj):
  return objectStoreMemoryClass()

