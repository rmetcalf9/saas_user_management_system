# Description of Tenant Object
from constants import authProviderNotFoundException
import json
import copy

#designed as immutable object
class personClass():
  _mainDict = None
  _jsonRepersentation = None
  _objectVersion = None
  def __init__(self, JSONRetrievedFromStore, objectVersion):
    self._mainDict = copy.deepcopy(JSONRetrievedFromStore)
    self._objectVersion = objectVersion
  
  def _generateJSONRepresenationAndStoreItInCache(self):
    aa = self._mainDict.copy()
    self._jsonRepersentation = aa
  
  def getJSONRepresenation(self):
    if self._jsonRepersentation is None:
      self._generateJSONRepresenationAndStoreItInCache()
    return self._jsonRepersentation

  def getObjectVersion(self):
    return self._objectVersion

  #Callers should not expect to update this
  def getReadOnlyDict(self):
    return self._mainDict
