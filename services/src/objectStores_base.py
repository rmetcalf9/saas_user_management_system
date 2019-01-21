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
  
  def getObjectJSON(self, appObj, objectType, objectKey):
    return self._getObjectJSON(appObj, objectType, objectKey)
  
  def _saveJSONObject(self, appObj, objectType, objectKey, JSONString):
    raise Exception('Not Implemented')
  def _removeJSONObject(self, appObj, objectType, objectKey):
    raise Exception('Not Implemented')
  def _updateJSONObject(self, appObj, objectType, objectKey, updateFn):
    raise Exception('Not Implemented')
  def _getObjectJSON(self, appObj, objectType, objectKey):
    raise Exception('Not Implemented')
