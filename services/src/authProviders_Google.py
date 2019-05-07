#Auth provider that links with google login
from authProviders_base import authProvider, InvalidAuthConfigException
import constants
import json

def loadStaticData(fileName):
  try:
    ##print('authProviderGoogle loadStaticData')
    with open(fileName, 'r') as f:
      return json.load(f)
  except FileNotFoundError:
    raise constants.customExceptionClass('Google secret file not found - ' + fileName,'InvalidAuthConfigException')


class authProviderGoogle(authProvider):
  secretJSONDownloadedFromGoogle = None
  def __init__(self, dataDict, guid, tenantName):
    super().__init__(dataDict, guid, tenantName)

    if 'clientSecretJSONFile' not in dataDict['ConfigJSON']:
      raise InvalidAuthConfigException
    
    #Only load the static data once
    if not self.hasStaticData():
      print('Static data not present loading')
      staticDataValue = {
        'secretJSONDownloadedFromGoogle': loadStaticData(dataDict['ConfigJSON']['clientSecretJSONFile'])
      }
      self.setStaticData(staticDataValue)
      if self.getStaticData()['secretJSONDownloadedFromGoogle'] is None:
        raise constants.customExceptionClass('loadStaticData returned None','InvalidAuthConfigException')

      if "web" not in self.getStaticData()['secretJSONDownloadedFromGoogle']:
        raise constants.customExceptionClass('Google secret file invliad (missing web)','InvalidAuthConfigException')
      if "client_id" not in self.getStaticData()['secretJSONDownloadedFromGoogle']["web"]:
        raise constants.customExceptionClass('Google secret file invliad (missing client_id)','InvalidAuthConfigException')
    #else:
    #  print('authProviderGoogle static data present NOT loading')


    #self.operationFunctions['ResetPassword'] = {
    #  'fn': self._executeAuthOperation_resetPassword,
    #  'requiredDictElements': ['newPassword']
    #}

  def __getClientID(self):
    return self.getStaticData()['secretJSONDownloadedFromGoogle']["web"]["client_id"]

  def _authSpercificInit(self):
    pass

  def getPublicStaticDataDict(self):
    return {"client_id": self.__getClientID()}
