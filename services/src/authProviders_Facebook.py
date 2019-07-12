#see https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow
from authProviders_base import authProvider, InvalidAuthConfigException
import constants
import json

def loadStaticData(fileName):
  try:
    ##print('authProviderGoogle loadStaticData')
    with open(fileName, 'r') as f:
      return json.load(f)
  except FileNotFoundError:
    raise constants.customExceptionClass('Facebook secret file not found - ' + fileName,'InvalidAuthConfigException')


class authProviderFacebook(authProvider):
  def __init__(self, dataDict, guid, tenantName, tenantObj, appObj):
    super().__init__(dataDict, guid, tenantName, tenantObj, appObj)

    if 'clientSecretJSONFile' not in dataDict['ConfigJSON']:
      raise InvalidAuthConfigException

    #Only load the static data once
    if not self.hasStaticData():
      #print('Static data not present loading')
      staticDataValue = {
        'secretJSON': loadStaticData(dataDict['ConfigJSON']['clientSecretJSONFile']),
      }
      self.setStaticData(staticDataValue)
      if self.getStaticData()['secretJSON'] is None:
        raise constants.customExceptionClass('loadStaticData returned None','InvalidAuthConfigException')

      if "web" not in self.getStaticData()['secretJSON']:
        raise constants.customExceptionClass('Facebook secret file invliad (missing web)','InvalidAuthConfigException')
      if "client_id" not in self.getStaticData()['secretJSON']["web"]:
        raise constants.customExceptionClass('Facebook secret file invliad (missing client_id)','InvalidAuthConfigException')
      if "client_secret" not in self.getStaticData()['secretJSON']["web"]:
        raise constants.customExceptionClass('Facebook secret file invliad (missing client_id)','InvalidAuthConfigException')

  def _makeKey(self, credentialDICT):
    if 'code' not in credentialDICT:
      raise InvalidAuthConfigException
    if 'creds' not in credentialDICT:
      raise InvalidAuthConfigException
    return credentialDictGet_unique_user_id(credentialDICT) + constants.uniqueKeyCombinator + 'facebook'

  def __getClientID(self):
    return self.getStaticData()['secretJSON']["web"]["client_id"]

  def _authSpercificInit(self):
    pass

  def getPublicStaticDataDict(self):
    return {"client_id": self.__getClientID()}

  #check the auth and if it is not valid raise authFailedException
  def _auth(self, appObj, obj, credentialDICT):
    #not required as auths are checked at the enrichment stage
    pass

  def _getTypicalAuthData(self, credentialDICT):
    print("_getTypicalAuthData")
    raise Exception("Not Implemented yet")

  def _getAuthData(self, appObj, credentialDICT):
    print("_getAuthData")
    raise Exception("Not Implemented yet")

  def _enrichCredentialDictForAuth(self, credentialDICT):
    print("_enrichCredentialDictForAuth")
    raise Exception("Not Implemented yet")

  def _AuthActionToTakeWhenThereIsNoRecord(self, credentialDICT, storeConnection):
    print("_AuthActionToTakeWhenThereIsNoRecord")
    raise Exception("Not Implemented yet")
