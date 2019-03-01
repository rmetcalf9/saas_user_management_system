# Code to save JSON objects into a store.
#  Allows abstraction of particular store
#  This is the baseClass other stores inherit from
StoringNoneObjectAfterUpdateOperationException = Exception('Storing None Object After Update Operation')
SavedObjectShouldNotContainObjectVersionException = Exception('SavedObjectShouldNotContainObjectVersion')

class WrongObjectVersionExceptionClass(Exception):
  pass
WrongObjectVersionException = WrongObjectVersionExceptionClass('Wrong object version supplied - Has another change occured since loading?')


#Base class for object store
class ObjectStore():
  #if object version is set to none object version checking is turned off
  # object version may be a number or a guid depending on store technology
  

  #Return value is objectVersion of object saved
  def saveJSONObject(self, appObj, objectType, objectKey, JSONString, objectVersion = None):
    if 'ObjectVersion' in JSONString:
      raise SavedObjectShouldNotContainObjectVersionException
    return self._saveJSONObject(appObj, objectType, objectKey, JSONString, objectVersion)

  #Return value is None
  def removeJSONObject(self, appObj, objectType, objectKey, objectVersion = None, ignoreMissingObject = False):
    return self._removeJSONObject(appObj, objectType, objectKey, objectVersion, ignoreMissingObject)

  # Update the object in single operation. make transaction safe??
  # Return value is same as saveJSONobject
  def updateJSONObject(self, appObj, objectType, objectKey, updateFn, objectVersion = None):
    return self._updateJSONObject(appObj, objectType, objectKey, updateFn, objectVersion)
  
  #Return value is objectDICT, ObjectVersion, creationDate, lastUpdateDate
  #Return None, None, None, None if object isn't in store
  def getObjectJSON(self, appObj, objectType, objectKey):
    return self._getObjectJSON(appObj, objectType, objectKey)
  
  def getPaginatedResult(self, appObj, objectType, paginatedParamValues, request, outputFN=None):
    def defOutput(item):
      return item
    def defFilter(item, whereClauseText):
      return True
    if outputFN is None:
      outputFN = defOutput
    return self._getPaginatedResult(appObj, objectType, paginatedParamValues, request, outputFN)
  
  def _saveJSONObject(self, appObj, objectType, objectKey, JSONString, objectVersion):
    raise Exception('Not Overridden')
  def _removeJSONObject(self, appObj, objectType, objectKey, objectVersion, ignoreMissingObject):
    raise Exception('Not Overridden')
  def _updateJSONObject(self, appObj, objectType, objectKey, updateFn, objectVersion):
    raise Exception('Not Overridden')
  def _getObjectJSON(self, appObj, objectType, objectKey):
    raise Exception('Not Overridden')
  def _getPaginatedResult(self, appObj, objectType, paginatedParamValues, request, outputFN):
    raise Exception('Not Overridden')
