#see https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow
from authProviders_base import authProvider, InvalidAuthConfigException
import constants
import json
import requests

#def credentialDictGet_email(credentialDICT):
#  return credentialDICT["creds"]["id_token"]["email"]
#def credentialDictGet_emailVerfied(credentialDICT):
#  return credentialDICT["creds"]["id_token"]["email_verified"]
#def credentialDictGet_known_as(credentialDICT):
#  return credentialDICT["creds"]["id_token"]["given_name"]
def credentialDictGet_unique_user_id(credentialDICT):
  print(credentialDICT)
  return credentialDICT["authResponse"]["userID"]


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

  def _AuthActionToTakeWhenThereIsNoRecord(self, credentialDICT, storeConnection):
    try:
      self.appObj.RegisterUserFn(self.tenantObj, self.guid, credentialDICT, "authProviders_Facebook/_AuthActionToTakeWhenThereIsNoRecord", storeConnection)
    except constants.customExceptionClass as err:
      if err.id == 'userCreationNotAllowedException':
        return #Do nothing
      raise err

  def _enrichCredentialDictForAuth(self, credentialDICT):
    # This process MUST verify the token we got from facebook is Invalid
    #  otherwise users can send anything and pretend they logged into
    #  facebook as anyone!
    print("_enrichCredentialDictForAuth - Partially Implemented")

    '''
    print("input credentialDICT:", credentialDICT)
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

    #From DOCS
    #GET https://graph.facebook.com/v3.3/oauth/access_token?
    #   client_id={app-id}
    #   &redirect_uri={redirect-uri}
    #   &client_secret={app-secret}
    #   &code={code-parameter}

    urlToGet = "https://graph.facebook.com/me?fields=id&"
    urlToGet += "access_token=" + credentialDICT["authResponse"]["accessToken"]

    print("URL to make get to call is:", urlToGet)

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
    print("Got result status code:", result.status_code)
    print("Got result text:", result.text)

    resultDICT = json.loads(result.text)
    print("resultDICT:", resultDICT)

    if resultDICT["id"] == credentialDICT["authResponse"]["userID"]:
      print("ID MATCH")
    else:
      print("ID MISMATCH")

    raise Exception("Rest Not Implemented yet")

  def _getTypicalAuthData(self, credentialDICT):
    print("_getTypicalAuthData")
    raise Exception("Not Implemented yet")

  def _getAuthData(self, appObj, credentialDICT):
    print("_getAuthData")
    raise Exception("Not Implemented yet")
