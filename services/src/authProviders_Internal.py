#Provides auth provider functions
from authProviders_base import authProvider, InvalidAuthConfigException
from constants import uniqueKeyCombinator, masterInternalAuthTypePassword, authFailedException
from base64 import b64decode

def getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(appObj, username, password, tenantAuthProvSalt):
  masterSecretKey = (username + ":" + password + ":AG44")
  return appObj.bcrypt.hashpw(masterSecretKey, b64decode(tenantAuthProvSalt))

class authProviderInternal(authProvider):
  def _authSpercificInit(self):
    if 'userSufix' not in self.configJSON:
      raise InvalidAuthConfigException

  def _makeKey(self, authTypeConfigDict):
    if 'username' not in authTypeConfigDict:
      raise InvalidAuthConfigException
    return authTypeConfigDict['username'] + self.configJSON['userSufix'] + uniqueKeyCombinator + self.authProviderType

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
    if 'password' not in credentialJSON:
      raise InvalidAuthConfigException
    hashedPass = self.hashPassword(appObj, credentialJSON['password'], obj["AuthProviderJSON"]['salt'])
    if hashedPass != obj["AuthProviderJSON"]['password']:
      raise authFailedException

