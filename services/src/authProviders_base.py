#Base class for all authProviders
# An auth has mutiple identities
#  an identity has one user
tryingToCreateDuplicateAuthException = Exception('Trying To Create Duplicate Auth (Matching username)')
from constants import authFailedException


class authProvider():
  authProviderType = None
  configJSON = None
  def __init__(self, authProviderType, configJSON):
    self.authProviderType = authProviderType
    self.configJSON = configJSON

  def _makeKey(self, username):
    raise NotOverriddenException

  def _AddAuthForIdentity(self, username):
    raise NotOverriddenException

  def Auth(self, appObj, credentialJSON):
    raise NotOverriddenException

  def AddAuth(self, appObj, userInfoToStoreDict, personGUID):
    key = self._makeKey(userInfoToStoreDict['username'])
    obj = appObj.objectStore.getObjectJSON(appObj,"userAuths", key)
    if obj is not None:
      raise tryingToCreateDuplicateAuthException

    mainObjToStore = {
      "AuthUserKey": key,
      "AuthProviderType": self.authProviderType,
      "AuthProviderJSON": self._getAuthData(appObj, userInfoToStoreDict),
      "personGUID": personGUID
    }
    appObj.objectStore.saveJSONObject(appObj,"userAuths",  self._makeKey(userInfoToStoreDict['username']), mainObjToStore)
    
    return mainObjToStore

  def Auth(self, appObj, credentialJSON):
    obj = appObj.objectStore.getObjectJSON(appObj,"userAuths", self._makeKey(credentialJSON['username']))
    if obj is None:
      raise authFailedException
    self._auth(appObj, obj, credentialJSON)
    return obj

