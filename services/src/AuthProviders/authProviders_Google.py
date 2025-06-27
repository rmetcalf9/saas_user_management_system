#Auth provider that links with google login
from .authProviders_base import authProvider, InvalidAuthConfigException
import constants
import json
from .Exceptions import CustomAuthProviderExceptionClass

##from google_auth_oauthlib.flow import InstalledAppFlow
##from oauth2client.client import flow_from_clientsecrets
from oauth2client import client
# https://google-auth.readthedocs.io/en/latest/index.html?highlight=google-auth
# https://developers.google.com/api-client-library/python/guide/aaa_oauth

def loadStaticData(fileName):
  try:
    ##print('authProviderGoogle loadStaticData')
    with open(fileName, 'r') as f:
      return json.load(f)
  except FileNotFoundError:
    raise CustomAuthProviderExceptionClass('Google secret file not found - ' + fileName, 'InvalidAuthConfigException')

'''
Eample
{
"code": "AAA",
"creds": {
"access_token": "XXX",
"client_id": "XXX",
"client_secret": "XXX",
"refresh_token": "XXX",
"token_expiry": "2019-05-08T14:55:14Z",
"token_uri": "https://oauth2.googleapis.com/token",
"user_agent": null,
"revoke_uri": "https://oauth2.googleapis.com/revoke",
"id_token": {
  "iss": "https://accounts.google.com",
  "azp": "???.apps.googleusercontent.com",
  "aud": "???.apps.googleusercontent.com",
  "sub": "56454656465454",
  "email": "rmetcalf9@googlemail.com",
  "email_verified": true,
  "at_hash": "???",
  "name": "Robert Metcalf",
  "picture": "https://lh6.googleusercontent.com/dsaddsaffs/s96-c/photo.jpg",
  "given_name": "Robert",
  "family_name": "Metcalf",
  "locale": "en-GB",
  "iat": 342543,
  "exp": 324324
},
}
'''
def credentialDictGet_email(credentialDICT):
  return credentialDICT["creds"]["id_token"]["email"]
def credentialDictGet_emailVerfied(credentialDICT):
  return credentialDICT["creds"]["id_token"]["email_verified"]
def credentialDictGet_known_as(credentialDICT):
  return credentialDICT["creds"]["id_token"]["given_name"]
def credentialDictGet_unique_user_id(credentialDICT):
  return credentialDICT["creds"]["id_token"]["sub"]

class authProviderGoogle(authProvider):
  def _getTypicalAuthData(self, credentialDICT):
    return {
      "user_unique_identifier": credentialDictGet_email(credentialDICT) + '@' + self.guid, #used for username - needs to be unique across all auth provs
      "known_as": credentialDictGet_known_as(credentialDICT), #used to display in UI for the user name
      "other_data": {
        "email": credentialDICT["creds"]["id_token"]["email"],
        "email_verified": credentialDICT["creds"]["id_token"]["email_verified"],
        "name": credentialDICT["creds"]["id_token"]["name"],
        "picture": credentialDICT["creds"]["id_token"]["picture"],
        "given_name": credentialDICT["creds"]["id_token"]["given_name"],
        "family_name": credentialDICT["creds"]["id_token"]["family_name"],
        "locale": credentialDICT["creds"]["id_token"]["locale"]
      } #Other data like name full name that can be provided - will vary between auth providers
    }
  def _getAuthData(self, appObj, credentialDICT):
    return {
      "email": credentialDICT["creds"]["id_token"]["email"],
      "email_verified": credentialDICT["creds"]["id_token"]["email_verified"],
      "name": credentialDICT["creds"]["id_token"]["name"],
      "picture": credentialDICT["creds"]["id_token"]["picture"],
      "given_name": credentialDICT["creds"]["id_token"]["given_name"],
      "family_name": credentialDICT["creds"]["id_token"]["family_name"],
      "locale": credentialDICT["creds"]["id_token"]["locale"]
    }

  def __init__(self, dataDict, guid, tenantName, tenantObj, appObj):
    super().__init__(dataDict, guid, tenantName, tenantObj, appObj)

    if 'clientSecretJSONFile' not in dataDict['ConfigJSON']:
      raise InvalidAuthConfigException

    #Only load the static data once
    if not self.hasStaticData():
      #print('Static data not present loading')
      staticDataValue = {
        'secretJSONDownloadedFromGoogle': loadStaticData(dataDict['ConfigJSON']['clientSecretJSONFile']),
#        'flow': flow_from_clientsecrets(
#          dataDict['ConfigJSON']['clientSecretJSONFile'],
#          scope='https://www.googleapis.com/auth/userinfo.email',
#          redirect_uri='https://localhost'
#        )
#        'flow': InstalledAppFlow.from_client_secrets_file(
#          dataDict['ConfigJSON']['clientSecretJSONFile'],
#          scopes=['https://www.googleapis.com/auth/userinfo.email']
#        )
      }
      self.setStaticData(staticDataValue)
      if self.getStaticData()['secretJSONDownloadedFromGoogle'] is None:
        raise constants.customExceptionClass('loadStaticData returned None', 'InvalidAuthConfigException')

      if "web" not in self.getStaticData()['secretJSONDownloadedFromGoogle']:
        raise constants.customExceptionClass('Google secret file invliad (missing web)', 'InvalidAuthConfigException')
      if "client_id" not in self.getStaticData()['secretJSONDownloadedFromGoogle']["web"]:
        raise constants.customExceptionClass('Google secret file invliad (missing client_id)', 'InvalidAuthConfigException')

    #else:
    #  print('authProviderGoogle static data present NOT loading')


    #self.operationFunctions['ResetPassword'] = {
    #  'fn': self._executeAuthOperation_resetPassword,
    #  'requiredDictElements': ['newPassword']
    #}

  def _makeKey(self, credentialDICT):
    if 'code' not in credentialDICT:
      raise InvalidAuthConfigException
    if 'creds' not in credentialDICT:
      raise InvalidAuthConfigException
    return credentialDictGet_unique_user_id(credentialDICT) + constants.uniqueKeyCombinator + 'google'

  def __getClientID(self):
    return self.getStaticData()['secretJSONDownloadedFromGoogle']["web"]["client_id"]

  def _authSpercificInit(self):
    pass

  def getPublicStaticDataDict(self):
    return {"client_id": self.__getClientID()}

  def _enrichCredentialDictForAuth(self, credentialDICT, appObj):
    credentials = None
    try:
      ##credentials = self.getStaticData()['flow'].run_console()
      ##credentials = self.getStaticData()['flow'].step2_exchange(credentialDICT['code'])
      ##credentials = client.credentials_from_clientsecrets_and_code(
      ##  self.dataDict['ConfigJSON']['clientSecretJSONFile'],
      ##  ['profile', 'email'],
      ##  credentialDICT['code']
      ##)

      # Default to 'postmessage' for browser-based flows (used by frontend)
      redirect_uri = 'postmessage'
      if "redirect_uri" in credentialDICT:
        if isinstance(credentialDICT["redirect_uri"], str):
          if len(credentialDICT["redirect_uri"]) < 4096:
            SAFE_PREFIXES = ('http://localhost', 'https://localhost')
            if credentialDICT["redirect_uri"].startswith(SAFE_PREFIXES):
              redirect_uri = credentialDICT["redirect_uri"]
      credentials = client.credentials_from_code(
        client_id = self.getStaticData()['secretJSONDownloadedFromGoogle']["web"]["client_id"],
        client_secret  = self.getStaticData()['secretJSONDownloadedFromGoogle']["web"]["client_secret"],
        scope = ['profile', 'email'],
        code = credentialDICT['code'],
        redirect_uri=redirect_uri
      )

    except Exception as err:
      print(err) # for the repr
      print(str(err)) # for just the message
      print(err.args) # the arguments that the exception has been called with.
      raise services.src.constants.authFailedException

    #print("credentials:", credentials.to_json())
    #raise Exception('Call to google to get code')
    return {
      "code": credentialDICT["code"],
      "creds": json.loads(credentials.to_json())
    }

  def _AuthActionToTakeWhenThereIsNoRecord(self, credentialDICT, storeConnection, ticketObj, ticketTypeObj):
    #if not self.getAllowUserCreation():
    #  return
    #if not self.tenantObj.getAllowUserCreation():
    #  return
    #Allow user creation checks preformed in RegisterUser call
    #print("Passed checks - will do thingy:")
    try:
      self.appObj.RegisterUserFn(self.tenantObj, self.guid, credentialDICT, "authProviders_Google/_AuthActionToTakeWhenThereIsNoRecord", storeConnection, ticketObj, ticketTypeObj)
    except constants.customExceptionClass as err:
      if err.id == 'userCreationNotAllowedException':
        return #Do nothing
      raise err
    #print("Email:", credentialDictGet_email(credentialDICT))
    #print("Email Veffied:", credentialDictGet_emailVerfied(credentialDICT))
    #print("known_as:", credentialDictGet_known_as(credentialDICT))

  #check the auth and if it is not valid raise authFailedException
  def _auth(self, appObj, obj, credentialDICT):
    #not required as auths are checked at the enrichment stage
    pass

  def canMakeKeyWithoutEnrichment(self):
    return False
