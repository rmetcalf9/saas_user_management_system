#Base class for all authProviders
# An auth has mutiple identities
#  an identity has one user
from constants import authFailedException, customExceptionClass

InvalidAuthConfigException = customExceptionClass('Invalid Auth Config','InvalidAuthConfigException')
tryingToCreateDuplicateAuthException = customExceptionClass('That username is already in use','tryingToCreateDuplicateAuthException')

def getAuthRecord(appObj, key):
  authRecord, objVer = appObj.objectStore.getObjectJSON(appObj,"userAuths", key)
  return authRecord


class authProvider():
  dataDict = None #See checks in init
  guid = None
  def __init__(self, dataDict, guid):
    if not 'ConfigJSON' in dataDict:
      raise Exception("ERROR No ConfigJSON supplied when creating authProvider")
    if not 'Type' in dataDict:
      raise Exception("ERROR No Type supplied when creating authProvider")
    if not 'AllowUserCreation' in dataDict:
      dataDict['AllowUserCreation'] = False
    self.dataDict = dataDict
    self._authSpercificInit()
    self.guid = guid
    
  def getType(self):
    return self.dataDict['Type']
  def getConfig(self):
    return self.dataDict['ConfigJSON']
  def getAllowUserCreation(self):
    return self.dataDict['AllowUserCreation']

  #Return the unique identifier for a particular auth
  def _makeKey(self, credentialDICT):
    raise NotOverriddenException

  def _AddAuthForIdentity(self, authTypeConfigDict):
    raise NotOverriddenException

  def _auth(self, appObj, credentialDICT):
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
      "AuthProviderType": self.dataDict["Type"],
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

