from authProviders_base import authProvider, InvalidAuthConfigException
import constants
import json
from Crypto.Cipher import AES
from Crypto.Random import OSRNG
from base64 import b64decode

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

  print("encryptPassword Salt:", salt)
  #salt is bytes or string
  #plain text is STRING
  #return value is bytes
  iv = OSRNG.posix.new().read(AES.block_size) #'This is an IV456'
  obj = AES.new(__INT__get32BytesFromSalt(salt), AES.MODE_CFB, iv)
  ciphertext = obj.encrypt(plainText)
  return (iv, ciphertext)

def decryptPassword(iv, cypherText, salt):
  if (type(salt)) is not bytes:
    salt = bytes(salt, 'utf-8')

  print("decryptPassword Salt:", salt)

  #recieved val is BYTES
  #returned val needs to be STRING
  obj2 = AES.new(__INT__get32BytesFromSalt(salt), AES.MODE_CFB, iv)
  decrypted = obj2.decrypt(cypherText)
  print("decrypted:", decrypted)
  return decrypted.decode("utf-8")

class authProviderLDAP(authProvider):
  def _getTypicalAuthData(self, credentialDICT):
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
  #def _AuthActionToTakeWhenThereIsNoRecord(self, credentialDICT, storeConnection):
  #  #if no user creation ERROR
  #  #else create auth
  #  raise Exception("_AuthActionToTakeWhenThereIsNoRecord not implemented")
  #(Tests exist for all cases here)

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
    print("     IV:", b64decode(credentialDICT['iv'].decode()))
    print("password:", b64decode(credentialDICT['password'].decode()))
    decryptedPass = decryptPassword(
      iv=b64decode(credentialDICT['iv'].decode()),
      cypherText=b64decode(credentialDICT['password'].decode()),
      salt=authProvObj["AuthProviderJSON"]['salt']
    )
    return True

  def __INT__isMemberOfRequiredGroups(self):
    return True

  #check the auth and if it is not valid raise authFailedException
  def _auth(self, appObj, obj, credentialDICT):
    credentialDICT2 = self.__INT__normaliseAndValidateCredentialDICT(credentialDICT)
    if not self.__INT__isValidUsernameAndPassword(appObj, obj, credentialDICT2):
      raise authFailedException
    if not self.__INT__isMemberOfRequiredGroups():
      raise authFailedException
