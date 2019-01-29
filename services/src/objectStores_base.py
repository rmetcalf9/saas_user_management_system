# Code to save JSON objects into a store.
#  Allows abstraction of particular store
#  This is the baseClass other stores inherit from
StoringNoneObjectAfterUpdateOperationException = Exception('StoringNoneObjectAfterUpdateOperation')

#Base class for object store
class ObjectStore():

  def saveJSONObject(self, appObj, objectType, objectKey, JSONString):
    return self._saveJSONObject(appObj, objectType, objectKey, JSONString)

  def removeJSONObject(self, appObj, objectType, objectKey):
    return self._removeJSONObject(appObj, objectType, objectKey)

  # Update the object in single operation. make transaction safe??
  def updateJSONObject(self, appObj, objectType, objectKey, updateFn):
    return self._updateJSONObject(appObj, objectType, objectKey, updateFn)
  
  #Return None if object isn't in store
  def getObjectJSON(self, appObj, objectType, objectKey):
    return self._getObjectJSON(appObj, objectType, objectKey)
  
  def getPaginatedResult(self, appObj, objectType, paginatedParamValues, request, outputFN=None, filterFN=None):
    def defOutput(item):
      return item
    def defFilter(item, whereClauseText):
      return True
    if outputFN is None:
      outputFN = defOutput
    if filterFN is None:
      filterFN = defFilter
    return self._getPaginatedResult(appObj, objectType, paginatedParamValues, request, outputFN, filterFN)
  
  def _saveJSONObject(self, appObj, objectType, objectKey, JSONString):
    raise Exception('Not Overridden')
  def _removeJSONObject(self, appObj, objectType, objectKey):
    raise Exception('Not Overridden')
  def _updateJSONObject(self, appObj, objectType, objectKey, updateFn):
    raise Exception('Not Overridden')
  def _getObjectJSON(self, appObj, objectType, objectKey):
    raise Exception('Not Overridden')
  def _getPaginatedResult(self, appObj, objectType, paginatedParamValues, request, outputFN, filterFN):
    raise Exception('Not Overridden')
