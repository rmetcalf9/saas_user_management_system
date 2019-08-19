from authProviders_base import authProvider, InvalidAuthConfigException
import constants
import json

class authProviderLDAP(authProvider):
  def _getTypicalAuthData(self, credentialDICT):
    raise Exception("_getTypicalAuthData not implemented")

  #LDAP will not need to store any data in the users record
  def _getAuthData(self, appObj, credentialDICT):
    return {}

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

  #check the auth and if it is not valid raise authFailedException
  def _auth(self, appObj, obj, credentialDICT):
    raise Exception("_auth not implemented")
