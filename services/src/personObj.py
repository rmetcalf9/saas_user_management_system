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

  def _linkExistantAuth(self, appObj, authDict, authProviderObj, credentialJSON, storeConnection):
    #As the auth exists we have TWO person records. This one and the one returned with the other auth object.
    # we need to decide what to do with the person records
    raise constants.notImplemented("personOBj._linkExistantAuth")


  def _linkNonExistantAuth(self, appObj, authProviderObj, credentialJSON, storeConnection, associatePersonWithAuthCalledWhenAuthIsCreated):
    return authProviderObj.AddAuth(
      appObj,
      credentialJSON,
      self.getGUID(),
      storeConnection,
      associatePersonWithAuthCalledWhenAuthIsCreated=associatePersonWithAuthCalledWhenAuthIsCreated
    )

  def linkAuth(self, appObj, authProviderObj, credentialJSON, storeConnection, associatePersonWithAuthCalledWhenAuthIsCreated):
    #Different logic if this is an existing auth vs if it is new

    authDict = None
    try:
      enrichedCredentialDICT = authProviderObj.ValaditeExternalCredentialsAndEnrichCredentialDictForAuth(credentialJSON, appObj)
      authDict, objVer, creationDateTime, lastUpdateDateTime = authProviderObj.AuthReturnAll(
        appObj, enrichedCredentialDICT, storeConnection, True,
        authTPL = None, authTPLQueried = False,
        ticketObj = None, ticketTypeObj = None
      )
    except constants.customExceptionClass as err:
      if err.id=="authNotFoundException":
        pass #Auth is not found so should be created
      elif err.id=="authFailedException":
        raise constants.customExceptionClass("Invalid credentials for auth to link with", "linkAuthFailedException")
      else:
        raise err

    if authDict is None:
      return self._linkNonExistantAuth(appObj, authProviderObj, enrichedCredentialDICT, storeConnection, associatePersonWithAuthCalledWhenAuthIsCreated=associatePersonWithAuthCalledWhenAuthIsCreated)
    else:
      return self._linkExistantAuth(appObj, authDict, authProviderObj, enrichedCredentialDICT, storeConnection)

  def getGUID(self):
    return self._mainDict['guid']
