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
    if 'userSufix' not in self.getConfig():
      raise InvalidAuthConfigException

  def _makeKey(self, credentialDICT):
    if 'username' not in credentialDICT:
      raise InvalidAuthConfigException
    #print(self.getConfig()['userSufix'])
    return credentialDICT['username'] + self.getConfig()['userSufix'] + uniqueKeyCombinator + self.getType()

  def hashPassword(self, appObj, password, salt):
    masterSecretKey = (masterInternalAuthTypePassword + "f" + appObj.APIAPP_MASTERPASSWORDFORPASSHASH)
    if (type(password)) is not bytes:
      #print(type(password))
      raise Exception('Password passed to hashPassword must be bytes')
      #password = bytes(password, 'utf-8')
    combo_password = password + salt + str.encode(masterSecretKey)
    hashed_password = appObj.bcrypt.hashpw(combo_password, salt)
    return hashed_password
  
  def _getAuthData(self, appObj, credentialDICT):
    self.__normalizeCredentialDICT(credentialDICT)
    salt = appObj.bcrypt.gensalt()
    objToStore = {
      "password": self.hashPassword(appObj, credentialDICT['password'], salt),
      "salt": salt
    }
    return objToStore

  def __normalizeCredentialDICT(self, credentialDICT):
    #When we get calls from API the password will be string
    # when we get calls from internal it is already bytes
    # this converts it to always be bytes
    if (type(credentialDICT['password'])) is not bytes:
      credentialDICT['password'] = bytes(credentialDICT['password'], 'utf-8')
    
  def _auth(self, appObj, obj, credentialDICT):
    if 'password' not in credentialDICT:
      raise InvalidAuthConfigException
    self.__normalizeCredentialDICT(credentialDICT)

    hashedPass = self.hashPassword(appObj, credentialDICT['password'], obj["AuthProviderJSON"]['salt'])
    if hashedPass != obj["AuthProviderJSON"]['password']:
      raise authFailedException

