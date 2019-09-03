#see https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow
from authProviders_base import authProvider, InvalidAuthConfigException
import constants
import json
import requests

def credentialDictGet_unique_user_id(credentialDICT):
  #print(credentialDICT)
  return credentialDICT["creds"]["userID"]
def credentialDictGet_unique_access_token(credentialDICT):
  #print(credentialDICT)
  return credentialDICT["creds"]["accessToken"]


def loadStaticData(fileName):
  try:
    ##print('authProviderFacebook loadStaticData')
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
      if "redirect_uri" not in self.getStaticData()['secretJSON']["web"]:
        raise constants.customExceptionClass('Facebook secret file invliad (missing redirect_uri)','InvalidAuthConfigException')
      if "auth_uri" not in self.getStaticData()['secretJSON']["web"]:
        raise constants.customExceptionClass('Facebook secret file invliad (missing auth_uri)','InvalidAuthConfigException')

  def _makeKey(self, credentialDICT):
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

  def _AuthActionToTakeWhenThereIsNoRecord(self, credentialDICT, storeConnection):
    try:
      print("Facebook: _AuthActionToTakeWhenThereIsNoRecord")
      self.appObj.RegisterUserFn(self.tenantObj, self.guid, credentialDICT, "authProviders_Facebook/_AuthActionToTakeWhenThereIsNoRecord", storeConnection)
    except constants.customExceptionClass as err:
      if err.id == 'userCreationNotAllowedException':
        return #Do nothing
      raise err

  def _enrichCredentialDictForAuth(self, credentialDICT, appObj):
    # This process MUST verify the token we got from facebook is Invalid
    #  otherwise users can send anything and pretend they logged into
    #  facebook as anyone!
    try:


      #print("_enrichCredentialDictForAuth - Partially Implemented")

      '''
      input credentialDICT: {
        'authResponse': {
          'accessToken': 'longlongstringoflettersandnumbers',
          'userID': '10217018159979944',
          'expiresIn': 6780,
          'signedRequest': 'longlongstringoflettersandnumbers',
          'reauthorize_required_in': 7776000,
          'data_access_expiration_time': 1570788420
        },
        'status': 'connected'
      }
      '''
      validCredentialDICT = True
      if "authResponse" not in credentialDICT:
        validCredentialDICT = False
      else:
        if "accessToken" not in credentialDICT["authResponse"]:
          validCredentialDICT = False
        if "userID" not in credentialDICT["authResponse"]:
          validCredentialDICT = False

      if not validCredentialDICT:
        #print("Invalid crecential DICT recieved")
        #print("input credentialDICT:", credentialDICT)
        print("Invalid credentialDICT passed to facebook login")
        raise constants.authFailedException

      # URL to make get to call is: https://graph.facebook.com/me?fields=id&access_token=longlongstringoflettersandnumbers
      #print("URL to make get to call is:", urlToGet)

      urlToGet = "https://graph.facebook.com/me?fields=id&"
      urlToGet += "access_token=" + credentialDICT["authResponse"]["accessToken"]

      result = requests.get(
        urlToGet,
        headers=None,
        cookies=None
      )
      '''
      Example result
      {
        "id": "ID_VALUE"
      }
      '''
      #print("Got result status code:", result.status_code)
      # Got result status code: 200
      #print("Got result text:", result.text)

      resultDICT = json.loads(result.text)
      # Got result text: {"id":"123"}
      #print("resultDICT:", resultDICT)
      # resultDICT: {'id': '123'}
      # ID MATCH

      if result.status_code != 200:
        print("Facebook serivce bad response")
        print(" Got result status_code:", result.status_code)
        print(" Got result text:", result.text)
        raise constants.authFailedException

      if resultDICT["id"] != credentialDICT["authResponse"]["userID"]:
        print("Facebook verify failed")
        raise constants.authFailedException

    except Exception as err:
      print("Facebook ERR)")
      print(err) # for the repr
      print(str(err)) # for just the message
      print(err.args) # the arguments that the exception has been called with.
      raise constants.authFailedException

    return {
      "creds": {
        "userID": credentialDICT["authResponse"]["userID"],
        "accessToken": credentialDICT["authResponse"]["accessToken"]
      }
    }

  def _getTypicalAuthData(self, credentialDICT):
    return {
      "user_unique_identifier": credentialDictGet_unique_user_id(credentialDICT) + '@' + self.guid, #used for username - needs to be unique across all auth provs
      "known_as": credentialDictGet_unique_user_id(credentialDICT), #used to display in UI for the user name
      "other_data": {}
    }

  def _getAuthData(self, appObj, credentialDICT):
    return {}
