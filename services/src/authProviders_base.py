#Base class for all authProviders
# An auth has mutiple identities
#  an identity has one user
from constants import authFailedException, customExceptionClass
import uuid
from persons import associatePersonWithAuthCalledWhenAuthIsCreated
from authsCommon import getAuthRecord

InvalidAuthConfigException = customExceptionClass('Invalid Auth Config','InvalidAuthConfigException')
tryingToCreateDuplicateAuthException = customExceptionClass('That username is already in use','tryingToCreateDuplicateAuthException')

#person.py also uses userAuths
  
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

  def _AddAuthForIdentity(self, credentialDICT):
    raise NotOverriddenException

  def _auth(self, appObj, credentialDICT):
    raise NotOverriddenException

  def _authSpercificInit(self):
    raise NotOverriddenException

  def AddAuth(self, appObj, credentialDICT, personGUID):
    key = self._makeKey(credentialDICT)
    obj, objVer, creationDateTime, lastUpdateDateTime = getAuthRecord(appObj, key)
    if obj is not None:
      #print('key:', key)
      raise tryingToCreateDuplicateAuthException

    mainObjToStore = {
      "AuthUserKey": key,
      "AuthProviderType": self.dataDict["Type"],
      "AuthProviderGUID": self.guid,
      "AuthProviderJSON": self._getAuthData(appObj, credentialDICT),
      "personGUID": personGUID
    }
    appObj.objectStore.saveJSONObject(appObj,"userAuths",  key, mainObjToStore)
    associatePersonWithAuthCalledWhenAuthIsCreated(appObj, personGUID, key)
    return mainObjToStore

  def Auth(self, appObj, credentialDICT):
    obj, objVer, creationDateTime, lastUpdateDateTime = getAuthRecord(appObj, self._makeKey(credentialDICT))
    if obj is None:
      raise authFailedException
    self._auth(appObj, obj, credentialDICT)
    return obj

  # Normally overridden
  def _getTypicalAuthData(self, credentialDICT):
    return {
      "user_unique_identifier": str(uuid.uuid4()), #used for username - needs to be unique across all auth provs
      "known_as": 'autoCreatedUser', #used to display in UI for the user name
      "other_data": {} #Other data like name full name that can be provided - will vary between auth providers
    }

  def getTypicalAuthData(self, credentialDICT):
    return self._getTypicalAuthData(credentialDICT)
   
    
