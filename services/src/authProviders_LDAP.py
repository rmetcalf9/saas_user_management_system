from authProviders_base import authProvider, InvalidAuthConfigException
import constants
import json
from Crypto.Cipher import AES
from Crypto.Random import OSRNG
from base64 import b64decode, b64encode
import ldap

#Communication is SSL and that should keep password secure
# extra security is added by encryptinhg it using the salt as a key
# https://pypi.org/project/pycrypto/

def __INT__get32BytesFromSalt(salt):
  retBytes = b''
  for x in range(0,32):
    idx = x % len(salt)
    retBytes = retBytes + salt[idx:(idx+1)]

  return retBytes

def encryptPassword(plainText, salt):
  if (type(salt)) is not bytes:
    salt = bytes(salt, 'utf-8')

  #salt is bytes or string
  #plain text is STRING
  #return value is bytes
  iv = OSRNG.posix.new().read(AES.block_size) #'This is an IV456'
  obj = AES.new(__INT__get32BytesFromSalt(salt), AES.MODE_CFB, iv)
  ciphertext = obj.encrypt(plainText)

  #output base64 encoded strings
  return (b64encode(iv).decode("utf-8"), b64encode(ciphertext).decode("utf-8"))

def decryptPassword(iv, cypherText, salt):
  if (type(salt)) is not bytes:
    salt = bytes(salt, 'utf-8')
  #iv and cypherText are base64 encoded strings
  ivi=b64decode(iv)
  cypherTexti=b64decode(cypherText)

  #recieved val is BYTES
  #returned val needs to be STRING
  obj2 = AES.new(__INT__get32BytesFromSalt(salt), AES.MODE_CFB, ivi)
  decrypted = obj2.decrypt(cypherTexti)
  return decrypted.decode("utf-8")

class authProviderLDAP(authProvider):
  def _getTypicalAuthData(self, credentialDICT):
    if 'username' not in credentialDICT:
      raise InvalidAuthConfigException
    if 'password' not in credentialDICT:
      raise InvalidAuthConfigException
    return {
      "user_unique_identifier": credentialDICT['username'] + self.getConfig()['userSufix'], #used for username - needs to be unique across all auth provs
      "known_as": credentialDICT['username'], #used to display in UI for the user name
      "other_data": {} #Other data like name full name that can be provided - will vary between auth providers
    }

    raise Exception("_getTypicalAuthData not implemented")

  #LDAP will not need to store any data in the authProvs record
  def _getAuthData(self, appObj, credentialDICT):
    return {
      "salt": appObj.bcrypt.gensalt()
    }

  def __init__(self, dataDict, guid, tenantName, tenantObj, appObj):
    super().__init__(dataDict, guid, tenantName, tenantObj, appObj, typeSupportsUserCreation=True)

  def _makeKey(self, credentialDICT):
    if 'username' not in credentialDICT:
      raise InvalidAuthConfigException
    return credentialDICT['username'] + self.getConfig()['userSufix'] + constants.uniqueKeyCombinator + self.getType()

  def __getClientID(self):
    raise Exception("__getClientID not implemented")

  def __INT__checkStringConfigParamPresent(self, name):
    if name not in self.getConfig():
      raise constants.customExceptionClass('Missing ' + name,'InvalidAuthConfigException')

  def _authSpercificInit(self):
    for x in [
        'Timeout',
        'Host', 'Port',
        'UserBaseDN', 'UserAttribute',
        'GroupBaseDN', 'GroupAttribute',
        'GroupMemberField', 'GroupWhiteList',
        'userSufix'
      ]:
      self.__INT__checkStringConfigParamPresent(x)

  #not needed as there is no enrichment. (LDAP won't give us a token for refresh
  # NOTE we don't store the password so with LDAP there is no way to refresh)
  #def _enrichCredentialDictForAuth(self, credentialDICT):
  #  raise Exception("_enrichCredentialDictForAuth not implemented")

  #No special action if there is no auth record - created if allowed
  def _AuthActionToTakeWhenThereIsNoRecord(self, credentialDICT, storeConnection):
    #Checks in registeruserfn
    #if not self.getAllowUserCreation():
    #  return
    #if not self.tenantObj.getAllowUserCreation():
    #  return
    try:
      self.appObj.RegisterUserFn(self.tenantObj, self.guid, credentialDICT, "authProviders_LDAP/_AuthActionToTakeWhenThereIsNoRecord", storeConnection)
    except constants.customExceptionClass as err:
      if err.id == 'userCreationNotAllowedException':
        return #Do nothing
      raise err

  def __INT__normaliseAndValidateCredentialDICT(self, credentialDICT):
    if 'username' not in credentialDICT:
      raise InvalidAuthConfigException
    if 'password' not in credentialDICT:
      raise InvalidAuthConfigException
    if (type(credentialDICT['password'])) is not bytes:
      credentialDICT['password'] = bytes(credentialDICT['password'], 'utf-8')
    if (type(credentialDICT['iv'])) is not bytes:
      credentialDICT['iv'] = bytes(credentialDICT['iv'], 'utf-8')
    return credentialDICT

  def __INT__isValidUsernameAndPassword(self, appObj, authProvObj, credentialDICT):
    decryptedPass = decryptPassword(
      iv=credentialDICT['iv'],
      cypherText=credentialDICT['password'],
      salt=authProvObj["AuthProviderJSON"]['salt']
    )

    username = credentialDICT['username'].strip()
    password = decryptedPass
    if username == "":
      return False
    if password == "":
      return False
    ldapConString = "ldaps://" + self.getConfig()['Host'] + ":" + self.getConfig()['Port']
    ldap_connection = ldap.initialize(ldapConString)
    ldap_connection.protocol_version = ldap.VERSION3
    ldap.OPT_NETWORK_TIMEOUT = self.getConfig()['Timeout']
    try:
      ldap_connection.simple_bind_s(self.getConfig()['UserAttribute'] + "=" + username + "," + self.getConfig()['UserBaseDN'], password)
    except ldap.INVALID_CREDENTIALS:
      return False
    except ldap.SERVER_DOWN:
      raise constants.customExceptionClass('Can''t connect to LDAP ' + ldapConString,'ExternalAuthProviderNotReachableException')

    return True

  def __INT__isMemberOfRequiredGroups(self):
    return True

  #check the auth and if it is not valid raise authFailedException
  def _auth(self, appObj, obj, credentialDICT):
    credentialDICT2 = self.__INT__normaliseAndValidateCredentialDICT(credentialDICT)
    if not self.__INT__isValidUsernameAndPassword(appObj, obj, credentialDICT2):
      raise constants.authFailedException
    if not self.__INT__isMemberOfRequiredGroups():
      raise constants.authFailedException
