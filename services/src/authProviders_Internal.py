#Provides auth provider functions
from authProviders_base import authProvider, InvalidAuthConfigException, MissingAuthCredentialsException, InvalidAuthCredentialsException
from constants import uniqueKeyCombinator, masterInternalAuthTypePassword, authFailedException
from base64 import b64decode, b64encode
from constants import customExceptionClass

def getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(appObj, username, password, tenantAuthProvSalt):
  #print("getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse called with:")
  #print(" - username:",username, ': (', type(username), ')')
  #print(" - password:",password, ': (', type(password), ')')
  #print(" - tenantAuthProvSalt:",tenantAuthProvSalt, ': (', type(tenantAuthProvSalt), ')')

  masterSecretKey = (username + ":" + password + ":AG44").encode()
  saltToUse = b64decode(tenantAuthProvSalt)
  res = appObj.bcrypt.hashpw(masterSecretKey, saltToUse)
  #print(" result:",res, ': (', type(res), ')')

  return res

def _INT_hashPassword(APIAPP_MASTERPASSWORDFORPASSHASH, bcryptObj, password, salt):
  #Used for debugging - not in main code as would be security risk
  #print("_INT_hashPassword call with:")
  #print(" - APIAPP_MASTERPASSWORDFORPASSHASH:", APIAPP_MASTERPASSWORDFORPASSHASH, ' (', type(APIAPP_MASTERPASSWORDFORPASSHASH), ')')
  #print(" - password:", password, ' (', type(password), ')')
  #print(" - salt:", salt, ' (', type(salt), ')')

  masterSecretKey = (masterInternalAuthTypePassword + "f" + APIAPP_MASTERPASSWORDFORPASSHASH)
  if (type(password)) is not bytes:
    #print(type(password))
    raise Exception('Password passed to hashPassword must be bytes')
    #password = bytes(password, 'utf-8')
  #raise Exception(type(salt))
  if (type(salt)) is not bytes:
    print ("ERROR Type of SALT is ", type(salt))
    print ("  - salt:", salt)
    raise Exception('Salt passed to hashPassword must be bytes')
  combo_password = password + salt + str.encode(masterSecretKey)
  hashed_password = bcryptObj.hashpw(combo_password, salt)

  #print("Resulting hashed password:")
  #print("hashed_password:", hashed_password, ' (', type(APIAPP_MASTERPASSWORDFORPASSHASH), ')')

  return hashed_password

class authProviderInternal(authProvider):
  def __init__(self, dataDict, guid, tenantName, tenantObj, appObj):
    super().__init__(dataDict, guid, tenantName, tenantObj, appObj)
    self.operationFunctions['ResetPassword'] = {
      'fn': self._executeAuthOperation_resetPassword,
      'requiredDictElements': ['newPassword']
    }

  def _authSpercificInit(self):
    if 'userSufix' not in self.getConfig():
      raise InvalidAuthConfigException

  def _makeKey(self, credentialDICT):
    if 'username' not in credentialDICT:
      raise MissingAuthCredentialsException
    #print(self.getConfig()['userSufix'])
    return credentialDICT['username'] + self.getConfig()['userSufix'] + uniqueKeyCombinator + self.getType()

  def _getAuthData(self, appObj, credentialDICT):
    #print("_getAuthData call with:")
    #print(" credentialDICT['password']:",credentialDICT['password'], ' (', type(credentialDICT['password']), ')')
    self.__normalizeCredentialDICT(credentialDICT)
    salt = appObj.bcrypt.gensalt()
    objToStore = {
      "password": _INT_hashPassword(appObj.APIAPP_MASTERPASSWORDFORPASSHASH, appObj.bcrypt, credentialDICT['password'], salt),
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
    #print("_getAuthData call with:")
    #print(" credentialDICT['password']:",credentialDICT['password'], ' (', type(credentialDICT['password']), ')')
    if 'password' not in credentialDICT:
      raise InvalidAuthCredentialsException
    self.__normalizeCredentialDICT(credentialDICT)

    hashedPass = _INT_hashPassword(appObj.APIAPP_MASTERPASSWORDFORPASSHASH, appObj.bcrypt, credentialDICT['password'], obj["AuthProviderJSON"]['salt'])
    if hashedPass != obj["AuthProviderJSON"]['password']:
      #print("DEBUG LING IN AUTHPROVIDERS_INTERNAL TO BE REMOVED")
      #print("Auth failed - hashedpass mismatch -")
      #print("RECANDHASHED=" + str(hashedPass))
      #print("      FROMDB=" + str(obj["AuthProviderJSON"]['password']))
      raise authFailedException

  def _getTypicalAuthData(self, credentialDICT):
    if 'username' not in credentialDICT:
      raise InvalidAuthConfigException
    return {
      "user_unique_identifier": credentialDICT['username'] + self.getConfig()['userSufix'], #used for username - needs to be unique across all auth provs
      "known_as": self.getDefaultKnownAs(credentialDICT), #used to display in UI for the user name
      "other_data": {} #Other data like name full name that can be provided - will vary between auth providers
    }

  def _getDefaultKnownAs(self, credentialDICT):
    return credentialDICT['username']


  def _executeAuthOperation_resetPassword(self, appObj, authObj, storeConnection, operationName, operationDICT):
    if (type(operationDICT["newPassword"])) is not bytes:
      operationDICT["newPassword"] = bytes(operationDICT["newPassword"], 'utf-8')

    newHashedPassword = _INT_hashPassword(appObj.APIAPP_MASTERPASSWORDFORPASSHASH, appObj.bcrypt, operationDICT["newPassword"], authObj['AuthProviderJSON']['salt'])
    if newHashedPassword == authObj['AuthProviderJSON']['password']:
      raise customExceptionClass('ERROR - New password matches origional','authopException')

    authObj['AuthProviderJSON']['password'] = newHashedPassword
    resultValue = {}
    return resultValue, authObj

  def requireRegisterCallToAutocreateUser(self):
    return True
