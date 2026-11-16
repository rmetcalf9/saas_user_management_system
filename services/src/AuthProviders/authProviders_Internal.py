#Provides auth provider functions
from .authProviders_base import authProvider, InvalidAuthConfigException, MissingAuthCredentialsException, InvalidAuthCredentialsException
from base64 import b64decode, b64encode
import constants
import uuid

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

import hashlib
import hmac

new_password_hash_version = 2
def _INT_hashPassword_for_new_passwords(APIAPP_MASTERPASSWORDFORPASSHASH, bcryptObj, password, salt):
  return hash_password(new_password_hash_version, APIAPP_MASTERPASSWORDFORPASSHASH, bcryptObj, password, salt)

def hash_password(hash_version, APIAPP_MASTERPASSWORDFORPASSHASH, bcryptObj, password, salt):
  if not isinstance(password, bytes):
    raise TypeError("Password must be bytes")

  if not isinstance(salt, bytes):
    raise TypeError("Salt must be bytes")

  if hash_version == 1:
    return _INT_hashPasswordLegacy(
      APIAPP_MASTERPASSWORDFORPASSHASH,
      bcryptObj,
      password,
      salt
    )
  elif hash_version == 2:
    return _INT_hashPasswordV2(
      APIAPP_MASTERPASSWORDFORPASSHASH,
      bcryptObj,
      password,
      salt
    )
  else:
    raise Exception("Unsupported password hash version: " + str(hash_version))

def _INT_hashPasswordLegacy(APIAPP_MASTERPASSWORDFORPASSHASH, bcryptObj, password, salt):
    """
    Original hashing algorithm.
    Reproduces the behaviour of bcrypt versions that silently truncated
    passwords longer than 72 bytes.
    """
    masterSecretKey = (
        constants.masterInternalAuthTypePassword
        + "f"
        + APIAPP_MASTERPASSWORDFORPASSHASH
    )
    combo_password = password + salt + str.encode(masterSecretKey)

    # Required for compatibility with existing bcrypt hashes.
    combo_password = combo_password[:72]

    return bcryptObj.hashpw(combo_password, salt)


def _INT_hashPasswordV2(APIAPP_MASTERPASSWORDFORPASSHASH, bcryptObj, password, salt):
  """
  Version 2 hashing algorithm.
  SHA-256 + Base64 preprocessing ensures bcrypt receives UTF-8-safe bytes.
  """

  masterSecretKey = (
          constants.masterInternalAuthTypePassword
          + "f"
          + APIAPP_MASTERPASSWORDFORPASSHASH
  )

  combo_password = password + salt + str.encode(masterSecretKey)

  # SHA-256 produces 32 binary bytes.
  digest = hashlib.sha256(combo_password).digest()

  # Base64 produces ASCII-compatible bytes (44 bytes).
  combo_password = b64encode(digest)

  return bcryptObj.hashpw(combo_password, salt)

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
    return credentialDICT['username'] + self.getConfig()['userSufix'] + constants.uniqueKeyCombinator + self.getType()

  def _getAuthData(self, appObj, credentialDICT):
    #print("_getAuthData call with:")
    #print(" credentialDICT['password']:",credentialDICT['password'], ' (', type(credentialDICT['password']), ')')
    self.__normalizeCredentialDICT(credentialDICT)
    salt = appObj.bcrypt.gensalt()
    objToStore = {
      "password": _INT_hashPassword_for_new_passwords(appObj.APIAPP_MASTERPASSWORDFORPASSHASH, appObj.bcrypt, credentialDICT['password'], salt),
      "salt": salt,
      "hashVersion": new_password_hash_version
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

    if obj["AuthProviderJSON"]['salt'].__class__.__name__ != "bytes":
      raise Exception("ERROR - authproviderJSON Salt retrieved from UserAuth in dynamoDB is not bytes - it is " + obj["AuthProviderJSON"]['salt'].__class__.__name__ )

    # get the hashversion but default to 1 if it is not there
    hashVersion = obj["AuthProviderJSON"].get('hashVersion', 1)

    hashedPass = hash_password(
      hash_version=hashVersion,
      APIAPP_MASTERPASSWORDFORPASSHASH=appObj.APIAPP_MASTERPASSWORDFORPASSHASH,
      bcryptObj=appObj.bcrypt,
      password=credentialDICT['password'],
      salt=obj["AuthProviderJSON"]['salt']
    )

    if not hmac.compare_digest(
            hashedPass,
            obj["AuthProviderJSON"]['password']
    ):
      raise constants.authFailedException

  def _getTypicalAuthData(self, credentialDICT):
    if 'username' not in credentialDICT:
      raise InvalidAuthConfigException
    return {
      "user_unique_identifier": str(uuid.uuid4()),
      "known_as": self.getDefaultKnownAs(credentialDICT), #used to display in UI for the user name
      "other_data": {} #Other data like name full name that can be provided - will vary between auth providers
    }

  def _getDefaultKnownAs(self, credentialDICT):
    return credentialDICT['username']


  def _executeAuthOperation_resetPassword(self, appObj, authObj, storeConnection, operationName, operationDICT):
    if (type(operationDICT["newPassword"])) is not bytes:
      operationDICT["newPassword"] = bytes(operationDICT["newPassword"], 'utf-8')

    new_password_hashed_with_old_method = hash_password(
      hash_version=authObj['AuthProviderJSON'].get('hashVersion', 1),
      APIAPP_MASTERPASSWORDFORPASSHASH=appObj.APIAPP_MASTERPASSWORDFORPASSHASH,
      bcryptObj=appObj.bcrypt,
      password=operationDICT["newPassword"],
      salt=authObj['AuthProviderJSON']['salt']
    )
    if hmac.compare_digest(
            new_password_hashed_with_old_method,
            authObj['AuthProviderJSON']['password']
    ):
      raise constants.customExceptionClass('ERROR - New password matches original','authopException')

    newSalt = appObj.bcrypt.gensalt()

    newHashedPassword = _INT_hashPassword_for_new_passwords(appObj.APIAPP_MASTERPASSWORDFORPASSHASH, appObj.bcrypt, operationDICT["newPassword"], newSalt)
    authObj['AuthProviderJSON']['password'] = newHashedPassword
    authObj['AuthProviderJSON']['salt'] = newSalt
    authObj['AuthProviderJSON']['hashVersion'] = new_password_hash_version
    resultValue = {}

    return resultValue, authObj

  def requireRegisterCallToAutocreateUser(self):
    return True
