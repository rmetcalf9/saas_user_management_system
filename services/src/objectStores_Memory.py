from objectStores_base import ObjectStore, StoringNoneObjectAfterUpdateOperationException

# Class that will store objects in memory only
class ObjectStore_Memory(ObjectStore):
  objectData = None
  objectDataAlternativeKeys = None
  def __init__(self):
    self.objectData = dict()
    self.objectDataAlternativeKeys = dict()
  def __getDictForObjectType(self, objectType):
    if objectType not in self.objectData:
      #print("Creating dict for " + objectType)
      self.objectData[objectType] = dict()
    return self.objectData[objectType]

  def _saveJSONObject(self, appObj, objectType, objectKey, JSONString):
    self.__getDictForObjectType(objectType)[objectKey] = JSONString
  def _removeJSONObject(self, appObj, objectType, objectKey):
    del self.__getDictForObjectType(objectType)[objectKey]

  # Update the object in single operation. make transaction safe??
  def _updateJSONObject(self, appObj, objectType, objectKey, updateFn):
    obj = self.getObjectJSON(appObj, objectType, objectKey)
    obj = updateFn(obj)
    if obj is None:
      raise StoringNoneObjectAfterUpdateOperationException
    self.saveJSONObject(appObj, objectType, objectKey, obj)
  
  def _getObjectJSON(self, appObj, objectType, objectKey):
    objectTypeDict = self.__getDictForObjectType(objectType)
    if objectKey in objectTypeDict:
      return objectTypeDict[objectKey]
    return None

  def _getPaginatedResult(self, appObj, objectType, paginatedParamValues, request, outputFN, filterFN):
    return appObj.getPaginatedResult(
      self.objectData[objectType],
      outputFN,
      request,
      filterFN
    )
