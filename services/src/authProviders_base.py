#Base class for all authProviders
# An auth has mutiple identities
#  an identity has one user
tryingToCreateDuplicateAuthException = Exception('Trying To Create Duplicate Auth (Matching username)')
from constants import authFailedException, customExceptionClass
from uuid import uuid4
from base64 import b64encode

InvalidAuthConfigException = customExceptionClass('Invalid Auth Config','InvalidAuthConfigException')

def _getAuthProviderJSON(appObj, guid, saltForPasswordHashing, menuText, iconLink, Type, AllowUserCreation, configJSON):
  return {
    "guid": guid,
    "MenuText": menuText,
    "IconLink": iconLink,
    "Type":  Type,
    "AllowUserCreation": AllowUserCreation,
    "ConfigJSON": configJSON,
    "saltForPasswordHashing": saltForPasswordHashing
  }

def getExistingAuthProviderJSON(appObj, existingJSON, menuText, iconLink, Type, AllowUserCreation, configJSON):
  return _getAuthProviderJSON(
    appObj, 
    existingJSON['guid'], 
    existingJSON['saltForPasswordHashing'], 
    menuText, iconLink, Type, AllowUserCreation, configJSON
  )

def getNewAuthProviderJSON(appObj, menuText, iconLink, Type, AllowUserCreation, configJSON):
  return _getAuthProviderJSON(
    appObj, str(uuid4()), str(b64encode(appObj.bcrypt.gensalt()),'utf-8'), 
    menuText, iconLink, Type, AllowUserCreation, configJSON
  )

class authProvider():
  authProviderType = None
  configJSON = None
  def __init__(self, authProviderType, configJSON):
    self.authProviderType = authProviderType
    self.configJSON = configJSON
    self._authSpercificInit()

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
    obj = appObj.objectStore.getObjectJSON(appObj,"userAuths", key)
    if obj is not None:
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
    obj = appObj.objectStore.getObjectJSON(appObj,"userAuths", self._makeKey(authTypeConfigDict))
    if obj is None:
      raise authFailedException
    self._auth(appObj, obj, authTypeConfigDict)
    return obj

