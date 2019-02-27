# Description of Tenant Object
from constants import authProviderNotFoundException
import json
import copy

#designed as immutable object
class personClass():
  _mainDict = None
  _jsonRepersentation = None
  _objectVersion = None
  _creationDateTime = None
  _lastUpdateDateTime = None
  _AssociatedUserObjs = None
  def __init__(self, JSONRetrievedFromStore, objectVersion, creationDateTime, lastUpdateDateTime, AssociatedUserObjs):
    self._mainDict = copy.deepcopy(JSONRetrievedFromStore)
    self._objectVersion = objectVersion
    self._creationDateTime = creationDateTime
    self._lastUpdateDateTime = lastUpdateDateTime
    self._AssociatedUserObjs = AssociatedUserObjs
  
  def _generateJSONRepresenationAndStoreItInCache(self):
    aa = self._mainDict.copy()
    aa['ObjectVersion'] = self._objectVersion
    aa['creationDateTime'] = self._creationDateTime
    aa['lastUpdateDateTime'] = self._lastUpdateDateTime
    associatedUsers = []
    for u in self._AssociatedUserObjs:
      associatedUsers.append(u.getJSONRepresenation())
    aa['associatedUsers'] = associatedUsers
    
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
