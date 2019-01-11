#Provides auth provider functions
from authProviders_base import authProvider
from constants import uniqueKeyCombinator, masterInternalAuthTypePassword, authFailedException

class authProviderInternal(authProvider):
  def _makeKey(self, username):
    return username + self.configJSON['userSufix'] + uniqueKeyCombinator + self.authProviderType

  def hashPassword(self, appObj, password, salt):
    masterSecretKey = (masterInternalAuthTypePassword + "f" + appObj.APIAPP_MASTERPASSWORDFORPASSHASH)
    combo_password = password.encode() + salt + masterSecretKey.encode()
    hashed_password = appObj.bcrypt.hashpw(combo_password, salt)
    return hashed_password
  
  def _getAuthData(self, appObj, userInfoToStoreDict):
    salt = appObj.bcrypt.gensalt()
    objToStore = {
      "password": self.hashPassword(appObj, userInfoToStoreDict['password'], salt),
      "salt": salt
    }
    return objToStore

  def _auth(self, appObj, obj, credentialJSON):
    hashedPass = self.hashPassword(appObj, credentialJSON['password'], obj["AuthProviderJSON"]['salt'])
    if hashedPass != obj["AuthProviderJSON"]['password']:
      raise authFailedException
