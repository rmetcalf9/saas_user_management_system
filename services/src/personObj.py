# Description of Tenant Object
import constants
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
  _authObjs = None
  def __init__(self, JSONRetrievedFromStore, objectVersion, creationDateTime, lastUpdateDateTime, AssociatedUserObjs, authObjs):
    self._mainDict = copy.deepcopy(JSONRetrievedFromStore)
    self._objectVersion = objectVersion
    self._creationDateTime = creationDateTime
    self._lastUpdateDateTime = lastUpdateDateTime
    self._AssociatedUserObjs = AssociatedUserObjs
    self._authObjs = authObjs
  
  def _generateJSONRepresenationAndStoreItInCache(self):
    aa = self._mainDict.copy()
    aa['ObjectVersion'] = self._objectVersion
    aa['creationDateTime'] = self._creationDateTime
    aa['lastUpdateDateTime'] = self._lastUpdateDateTime
    associatedUsers = []
    for u in self._AssociatedUserObjs:
      associatedUsers.append(u.getJSONRepresenation())
    aa['associatedUsers'] = associatedUsers
    aa['personAuths'] = self._authObjs
    
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

  def _linkExistantAuth(self, authDict, authProviderObj, credentialJSON, storeConnection):
    raise constants.notImplemented("personOBj._linkExistantAuth")


  def _linkNonExistantAuth(self, authProviderObj, credentialJSON, storeConnection):
    raise Exception("TODO auth that dosen't exist")

  def linkAuth(self, appObj, authProviderObj, credentialJSON, storeConnection):
    #Different logic if this is an existing auth vs if it is new
    
    authDict = None
    try:
      authDict = authProviderObj.Auth(appObj, credentialJSON, storeConnection, True)
    except constants.customExceptionClass as err:
      if err.id=="constants.authFailedException":
        pass
      if err.id=="authFailedException":
        raise constants.customExceptionClass("Invalid credentials for auth to link with", "linkAuthFailedException")
      else:
        raise err
    
    if authDict is None:
      return self._linkNonExistantAuth(authProviderObj, credentialJSON, storeConnection)
    else:
      return self._linkExistantAuth(authDict, authProviderObj, credentialJSON, storeConnection)
    
