#Provides auth provider functions
from authProviders_base import authProvider, InvalidAuthConfigException
from constants import uniqueKeyCombinator, masterInternalAuthTypePassword, authFailedException
from base64 import b64decode, b64encode

def getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(appObj, username, password, tenantAuthProvSalt):
  masterSecretKey = (username + ":" + password + ":AG44").encode()
  saltToUse = b64decode(tenantAuthProvSalt)
  return appObj.bcrypt.hashpw(masterSecretKey, saltToUse)

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
    if (type(password)) is not bytes:
      print(type(password))
      raise Exception('Password passed to hashPassword must be bytes')
      #password = bytes(password, 'utf-8')
    combo_password = password + salt + str.encode(masterSecretKey)
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
    passwordBytes = credentialJSON['password']
    if (type(passwordBytes)) is not bytes:
      passwordBytes = bytes(passwordBytes, 'utf-8')

    hashedPass = self.hashPassword(appObj, passwordBytes, obj["AuthProviderJSON"]['salt'])
    if hashedPass != obj["AuthProviderJSON"]['password']:
      raise authFailedException

