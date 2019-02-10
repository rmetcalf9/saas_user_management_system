from objectStores_base import ObjectStore, StoringNoneObjectAfterUpdateOperationException, WrongObjectVersionException

# Class that will store objects in memory only
class ObjectStore_Memory(ObjectStore):
  objectData = None
  def __init__(self):
    self.objectData = dict()

  def __getDictForObjectType(self, objectType):
    if objectType not in self.objectData:
      #print("Creating dict for " + objectType)
      self.objectData[objectType] = dict()
    return self.objectData[objectType]

#  #Check if the object version supplied is the currently stored object
#  def _checkObjectVersion(self, appObj, objectType, objectKey, curVersion):
#    if curVersion is None:
#      return
#    objectVersionDict = self.__getDictForObjectType(objectType)
#    if objectKey not in objectVersionDict:
#      raise WrongObjectVersionException
#    if objectVersionDict[objectKey][1] != curVersion:
#      raise WrongObjectVersionException

  def _saveJSONObject(self, appObj, objectType, objectKey, JSONString, objectVersion):
    dictForObjectType = self.__getDictForObjectType(objectType)
    newObjectVersion = None
    if objectKey not in dictForObjectType:
      newObjectVersion = 1
      dictForObjectType[objectKey] = (JSONString, newObjectVersion)
    else:
      if objectVersion is not None:
        if str(objectVersion) != str(dictForObjectType[objectKey][1]):
          raise WrongObjectVersionException
      newObjectVersion = int(objectVersion) + 1
    dictForObjectType[objectKey] = (JSONString, newObjectVersion)
    return newObjectVersion

  def _removeJSONObject(self, appObj, objectType, objectKey, objectVersion):
    dictForObjectType = self.__getDictForObjectType(objectType)
    if objectVersion is not None:
      if objectKey not in dictForObjectType:
        raise Exception('Deleting something that isn\'t there')
      if str(dictForObjectType[objectKey][1]) != str(objectVersion):
        raise WrongObjectVersionException
    del self.__getDictForObjectType(objectType)[objectKey]
    return None

  # Update the object in single operation. make transaction safe??
  def _updateJSONObject(self, appObj, objectType, objectKey, updateFn, objectVersion):
    obj, ver = self.getObjectJSON(appObj, objectType, objectKey)
    if objectVersion is None:
      #If object version is not supplied then assume update will not cause an error
      objectVersion = ver 
    if str(objectVersion) != str(ver):
      raise WrongObjectVersionException
    obj = updateFn(obj)
    if obj is None:
      raise StoringNoneObjectAfterUpdateOperationException
    return self.saveJSONObject(appObj, objectType, objectKey, obj, objectVersion)
  
  def _getObjectJSON(self, appObj, objectType, objectKey):
    objectTypeDict = self.__getDictForObjectType(objectType)
    if objectKey in objectTypeDict:
      return objectTypeDict[objectKey]
    return None, None

  def _getPaginatedResult(self, appObj, objectType, paginatedParamValues, request, outputFN, filterFN):
    return appObj.getPaginatedResult(
      self.objectData[objectType],
      outputFN,
      request,
      filterFN
    )
