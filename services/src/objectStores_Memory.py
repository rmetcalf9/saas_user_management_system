from objectStores_base import ObjectStore, ObjectStoreConnectionContext, StoringNoneObjectAfterUpdateOperationException, WrongObjectVersionException

class ConnectionContext(ObjectStoreConnectionContext):
  objectType = None
  def __init__(self, objectType):
    super(ConnectionContext, self).__init__()
    self.objectType = objectType

  #transactional memory not implemented
  def _startTransaction(self):
    pass
  def _commitTransaction(self):
    pass
  def _rollbackTransaction(self):
    pass

    
  def _saveJSONObject(self, objectType, objectKey, JSONString, objectVersion):
    dictForObjectType = self.objectType._INT_getDictForObjectType(objectType)
    curTimeValue = self.objectType.appObj.getCurDateTime()
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

  def _removeJSONObject(self, objectType, objectKey, objectVersion, ignoreMissingObject):
    dictForObjectType = self.objectType._INT_getDictForObjectType(objectType)
    if objectVersion is not None:
      if objectKey not in dictForObjectType:
        raise Exception('Deleting something that isn\'t there')
      if str(dictForObjectType[objectKey][1]) != str(objectVersion):
        raise WrongObjectVersionException
    if objectKey not in self.objectType._INT_getDictForObjectType(objectType):
      if ignoreMissingObject:
        return None
    del self.objectType._INT_getDictForObjectType(objectType)[objectKey]
    return None

  # Update the object in single operation. make transaction safe??
  ## updateFn gets two paramaters:
  ##  object
  ##  connection
  def _updateJSONObject(self, objectType, objectKey, updateFn, objectVersion):
    obj, ver, creationDateTime, lastUpdateDateTime = self.getObjectJSON(objectType, objectKey)
    if objectVersion is None:
      #If object version is not supplied then assume update will not cause an error
      objectVersion = ver 
    if str(objectVersion) != str(ver):
      raise WrongObjectVersionException
    obj = updateFn(obj, self)
    if obj is None:
      raise StoringNoneObjectAfterUpdateOperationException
    return self.saveJSONObject(objectType, objectKey, obj, objectVersion)
  
  def _getObjectJSON(self, objectType, objectKey):
    objectTypeDict = self.objectType._INT_getDictForObjectType(objectType)
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
    
    
  def _getPaginatedResult(self, objectType, paginatedParamValues, request, outputFN):
    ##print('objectStoresMemory._getPaginatedResult self.objectType.objectData[objectType]:', self.objectType.objectData[objectType])
    return self.objectType.appObj.getPaginatedResult(
      self.objectType.objectData[objectType],
      outputFN,
      request,
      self._filterFN
    )

# Class that will store objects in memory only
class ObjectStore_Memory(ObjectStore):
  objectData = None
  def __init__(self, configJSON, appObj):
    super(ObjectStore_Memory, self).__init__(appObj)
    self.objectData = dict()
    #Dict = (objDICT, objectVersion, creationDate, lastUpdateDate)

  def _INT_getDictForObjectType(self, objectType):
    if objectType not in self.objectData:
      #print("Creating dict for " + objectType)
      self.objectData[objectType] = dict()
    return self.objectData[objectType]

  def _getConnectionContext(self):
    return ConnectionContext(self)

