from objectStores_base import ObjectStore, StoringNoneObjectAfterUpdateOperationException, WrongObjectVersionException

# Class that will store objects in memory only
class ObjectStore_Memory(ObjectStore):
  objectData = None
  def __init__(self, configJSON):
    self.objectData = dict()
    #Dict = (objDICT, objectVersion, creationDate, lastUpdateDate)

  def __getDictForObjectType(self, objectType):
    if objectType not in self.objectData:
      #print("Creating dict for " + objectType)
      self.objectData[objectType] = dict()
    return self.objectData[objectType]

  def _saveJSONObject(self, appObj, objectType, objectKey, JSONString, objectVersion, transactionContext):
    dictForObjectType = self.__getDictForObjectType(objectType)
    curTimeValue = appObj.getCurDateTime()
    newObjectVersion = None
    if objectKey not in dictForObjectType:
      if objectVersion is not None:
        raise WrongObjectVersionException
      newObjectVersion = 1
      dictForObjectType[objectKey] = (JSONString, newObjectVersion, curTimeValue, curTimeValue)
    else:
      if objectVersion is not None:
        if str(objectVersion) != str(dictForObjectType[objectKey][1]):
          raise WrongObjectVersionException
      newObjectVersion = int(objectVersion) + 1
    dictForObjectType[objectKey] = (JSONString, newObjectVersion, dictForObjectType[objectKey][2], curTimeValue)
    return newObjectVersion

  def _removeJSONObject(self, appObj, objectType, objectKey, objectVersion, ignoreMissingObject, transactionContext):
    dictForObjectType = self.__getDictForObjectType(objectType)
    if objectVersion is not None:
      if objectKey not in dictForObjectType:
        raise Exception('Deleting something that isn\'t there')
      if str(dictForObjectType[objectKey][1]) != str(objectVersion):
        raise WrongObjectVersionException
    if objectKey not in self.__getDictForObjectType(objectType):
      if ignoreMissingObject:
        return None
    del self.__getDictForObjectType(objectType)[objectKey]
    return None

  # Update the object in single operation. make transaction safe??
  ## updateFn gets two paramaters:
  ##  object
  ##  transactionContext
  def _updateJSONObject(self, appObj, objectType, objectKey, updateFn, objectVersion, transactionContext):
    obj, ver, creationDateTime, lastUpdateDateTime = self.getObjectJSON(appObj, objectType, objectKey)
    if objectVersion is None:
      #If object version is not supplied then assume update will not cause an error
      objectVersion = ver 
    if str(objectVersion) != str(ver):
      raise WrongObjectVersionException
    obj = updateFn(obj, transactionContext)
    if obj is None:
      raise StoringNoneObjectAfterUpdateOperationException
    return self.saveJSONObject(appObj, objectType, objectKey, obj, objectVersion, transactionContext)
  
  def _getObjectJSON(self, appObj, objectType, objectKey):
    objectTypeDict = self.__getDictForObjectType(objectType)
    if objectKey in objectTypeDict:
      return objectTypeDict[objectKey]
    return None, None, None, None

  def _filterFN(self, item, whereClauseText):
    if whereClauseText is None:
      return True
    if whereClauseText == '':
      return True
    ###userDICT = CreateUserObjFromUserDict(appObj, item[0],item[1],item[2],item[3]).getJSONRepresenation()
    #TODO replace with a dict awear generic function
    #  we also need to consider removing spaces from consideration
    return whereClauseText in str(item).upper()
    
    
  def _getPaginatedResult(self, appObj, objectType, paginatedParamValues, request, outputFN):
    return appObj.getPaginatedResult(
      self.objectData[objectType],
      outputFN,
      request,
      self._filterFN
    )
