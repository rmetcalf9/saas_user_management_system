from authProviders_base import authProvider, InvalidAuthConfigException
import constants
import json

class authProviderLDAP(authProvider):
  def _getTypicalAuthData(self, credentialDICT):
    raise Exception("_getTypicalAuthData not implemented")

  def _getAuthData(self, appObj, credentialDICT):
    raise Exception("_getAuthData not implemented")

  def __init__(self, dataDict, guid, tenantName, tenantObj, appObj):
    super().__init__(dataDict, guid, tenantName, tenantObj, appObj)

  def _makeKey(self, credentialDICT):
    raise Exception("_makeKey not implemented")

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
        'GroupMemberField', 'GroupWhiteList'
      ]:
      self.__INT__checkStringConfigParamPresent(x)

  def getPublicStaticDataDict(self):
    raise Exception("getPublicStaticDataDict not implemented")

  def _enrichCredentialDictForAuth(self, credentialDICT):
    raise Exception("_enrichCredentialDictForAuth not implemented")

  def _AuthActionToTakeWhenThereIsNoRecord(self, credentialDICT, storeConnection):
    raise Exception("_AuthActionToTakeWhenThereIsNoRecord not implemented")

  #check the auth and if it is not valid raise authFailedException
  def _auth(self, appObj, obj, credentialDICT):
    raise Exception("_auth not implemented")
