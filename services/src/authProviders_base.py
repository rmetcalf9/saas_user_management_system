#Base class for all authProviders
# An auth has mutiple identities
#  an identity has one user
tryingToCreateDuplicateAuthException = Exception('Trying To Create Duplicate Auth (Matching username)')
from constants import authFailedException, customExceptionClass

InvalidAuthConfigException = customExceptionClass('Invalid Auth Config','InvalidAuthConfigException')

def getAuthRecord(appObj, key):
  authRecord, objVer = appObj.objectStore.getObjectJSON(appObj,"userAuths", key)
  return authRecord


class authProvider():
  authProviderType = None
  configJSON = None
  guid = None
  def __init__(self, authProviderType, configJSON, guid):
    self.authProviderType = authProviderType
    self.configJSON = configJSON
    self._authSpercificInit()
    self.guid = guid

  #Return the unique identifier for a particular auth
  def _makeKey(self, authTypeConfigDict):
    raise NotOverriddenException

  def _AddAuthForIdentity(self, authTypeConfigDict):
    raise NotOverriddenException

  def _auth(self, appObj, credentialJSON):
    raise NotOverriddenException

  def _authSpercificInit(self):
    raise NotOverriddenException

  def AddAuth(self, appObj, authTypeConfigDict, personGUID):
    key = self._makeKey(authTypeConfigDict)
    obj, objVer = appObj.objectStore.getObjectJSON(appObj,"userAuths", key)
    if obj is not None:
      #print('key:', key)
      raise tryingToCreateDuplicateAuthException

    mainObjToStore = {
      "AuthUserKey": key,
      "AuthProviderType": self.authProviderType,
      "AuthProviderJSON": self._getAuthData(appObj, authTypeConfigDict),
      "personGUID": personGUID
    }
    appObj.objectStore.saveJSONObject(appObj,"userAuths",  key, mainObjToStore)
    
    return mainObjToStore

  def Auth(self, appObj, authTypeConfigDict):
    obj = getAuthRecord(appObj, self._makeKey(authTypeConfigDict))
    if obj is None:
      raise authFailedException
    self._auth(appObj, obj, authTypeConfigDict)
    return obj

