#Provides auth provider functions
from constants import uniqueKeyCombinator, masterInternalAuthTypePassword
authFailed = Exception('AuthFailed')
import bcrypt


class authProvider():
  authProviderType = None
  configJSON = None
  def __init__(self, authProviderType, configJSON):
    self.authProviderType = authProviderType
    self.configJSON = configJSON
    
class authProviderInternal(authProvider):
  def _makeKey(self, username):
    return username + self.configJSON['userSufix'] + uniqueKeyCombinator + self.authProviderType
  def hashPassword(self, appObj, password, salt):
    masterSecretKey = (masterInternalAuthTypePassword + "f" + appObj.APIAPP_MASTERPASSWORDFORPASSHASH)
    combo_password = password.encode() + salt + masterSecretKey.encode()
    hashed_password = bcrypt.hashpw(combo_password, salt)
    return hashed_password
  
  
  def AddAuthForUser(self, appObj, UserID, userInfoToStoreJSON):
    salt = bcrypt.gensalt()
    objToStore = {
      "password": self.hashPassword(appObj, userInfoToStoreJSON['password'], salt),
      "salt": salt
    }
    key = self._makeKey(userInfoToStoreJSON['username'])
    mainObjToStore = {
      "AuthUserKey": key,
      "AuthProviderType": self.authProviderType,
      "UserID": UserID,
      "AuthProviderJSON": objToStore
    }
    appObj.objectStore.saveJSONObject(appObj,"userAuths",  self._makeKey(userInfoToStoreJSON['username']), mainObjToStore)

  def Auth(self, appObj, credentialJSON):
    obj = appObj.objectStore.getObjectJSON(appObj,"userAuths", self._makeKey(credentialJSON['username']))
    if obj is None:
      raise authFailed
    hashedPass = self.hashPassword(appObj, credentialJSON['password'], obj["AuthProviderJSON"]['salt'])
    if hashedPass != obj["AuthProviderJSON"]['password']:
      print(hashedPass)
      print(obj['password'])
      raise authFailed
    return obj["UserID"]
    
def authProviderFactory(type, configJSON):
  if type=='internal':
    return authProviderInternal('internal', configJSON)
  return None
  
  