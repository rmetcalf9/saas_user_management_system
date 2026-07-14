from .authProviders_base import authProvider, InvalidAuthConfigException
import constants
import copy
import requests
import json
from .Exceptions import CustomAuthProviderExceptionClass
import uuid
import jwt

'''
Example credentialDICT:
{
  "identityToken": "eyJraWQiOi..."
}
'''
def credentialDictGet_unique_user_id(credentialDICT):
  return credentialDICT["enriched"]["decodedjwt"]["sub"]

def decodeAppleJwtToken(identityToken, clientId, isAppRunningInTestingMode):
    keys = requests.get(constants.apple_signon_public_key_url).json()

    header = jwt.get_unverified_header(identityToken)
    if "kid" not in header:
        raise Exception("KID not found in JWT token")

    appleKey = None
    for key in keys["keys"]:
        if key["kid"] == header["kid"]:
            appleKey = key
            break

    if isAppRunningInTestingMode:
        if appleKey is None:
            if header["kid"] == constants.testmodersakeyforjwtsigning["kid"]:
                appleKey = constants.testmodersakeyforjwtsigning

    if appleKey is None:
        raise Exception("Apple signing key not found")

    decoded = jwt.decode(
        identityToken,
        jwt.PyJWK.from_dict(appleKey).key,
        algorithms=["RS256"],
        audience=clientId,
        issuer=constants.apple_iss
    )
    if "sub" not in decoded:
        raise Exception("Invalid Apple signing key - no sub")
    return decoded

class authProviderApple(authProvider):
    pass
    # def _getTypicalAuthData(self, credentialDICT):
    #     return {
    #         "user_unique_identifier": str(uuid.uuid4()),
    #         "known_as": credentialDictGet_known_as(credentialDICT),  # used to display in UI for the user name
    #         "other_data": {
    #             "email": credentialDICT["creds"]["id_token"].get("email", ""),
    #             "email_verified": credentialDICT["creds"]["id_token"].get("email_verified", False),
    #             "name": credentialDICT["creds"]["id_token"].get("name", ""),
    #             "picture": credentialDICT["creds"]["id_token"].get("picture", ""),
    #             "given_name": credentialDICT["creds"]["id_token"].get("given_name", ""),
    #             "family_name": credentialDICT["creds"]["id_token"].get("family_name", ""),
    #             "locale": credentialDICT["creds"]["id_token"].get("locale", locale_default)
    #         }  # Other data like name full name that can be provided - will vary between auth providers
    #     }
    #
    # def _getAuthData(self, appObj, credentialDICT):
    #     id_token = credentialDICT.get("creds", {}).get("id_token", {})
    #     return {
    #         "email": id_token.get("email"),
    #         "email_verified": id_token.get("email_verified", False),
    #         "name": id_token.get("name"),
    #         "picture": id_token.get("picture"),
    #         "given_name": id_token.get("given_name"),
    #         "family_name": id_token.get("family_name"),
    #         "locale": id_token.get("locale", locale_default),  # default to 'en' if missing
    #     }

    def __init__(self, dataDict, guid, tenantName, tenantObj, appObj):
        super().__init__(dataDict, guid, tenantName, tenantObj, appObj)
        if 'service_id' not in dataDict['ConfigJSON']:
            raise InvalidAuthConfigException

        if not isinstance(dataDict['ConfigJSON']['service_id'], str):
            raise InvalidAuthConfigException

        # Only load the static data once
        if not self.hasStaticData():
            # print('Static data not present loading')
            staticDataValue = {
            }
            self.setStaticData(staticDataValue)

    def _makeKey(self, credentialDICT):
        if 'identityToken' not in credentialDICT:
            raise InvalidAuthConfigException
        if 'creds' not in credentialDICT:
            raise InvalidAuthConfigException
        extra = ""
        if 'userSufix' in self.getConfig():
            extra += self.getConfig()['userSufix']
        return credentialDictGet_unique_user_id(credentialDICT) + extra + constants.uniqueKeyCombinator + 'apple'

    def __getClientID(self):
        #return self.getStaticData()['secretJSONDownloadedFromGoogle']["web"]["client_id"]
        return self.getConfig()["service_id"]

    def _authSpercificInit(self):
        pass

    def getPublicStaticDataDict(self):
        return {"client_id": self.__getClientID()}

    def _enrichCredentialDictForAuth(self, credentialDICT, appObj):
        try:
            retVal = copy.deepcopy(credentialDICT)
            if "identityToken" not in credentialDICT:
                raise constants.authFailedException
            retVal["enriched"] = {
                "decodedjwt": decodeAppleJwtToken(identityToken=credentialDICT["identityToken"], clientId=self.__getClientID(), isAppRunningInTestingMode=appObj.isAppRunningInTestingMode)
            }
            return retVal
        except Exception as err:
            # print(err)  # for the repr
            # print(str(err))  # for just the message
            # print(err.args)  # the arguments that the exception has been called with.
            raise constants.authFailedException

    # def _AuthActionToTakeWhenThereIsNoRecord(self, credentialDICT, storeConnection, ticketObj, ticketTypeObj):
    #     # if not self.getAllowUserCreation():
    #     #  return
    #     # if not self.tenantObj.getAllowUserCreation():
    #     #  return
    #     # Allow user creation checks preformed in RegisterUser call
    #     # print("Passed checks - will do thingy:")
    #     try:
    #         self.appObj.RegisterUserFn(self.tenantObj, self.guid, credentialDICT,
    #                                    "authProviders_Google/_AuthActionToTakeWhenThereIsNoRecord", storeConnection,
    #                                    ticketObj, ticketTypeObj)
    #     except constants.customExceptionClass as err:
    #         if err.id == 'userCreationNotAllowedException':
    #             return  # Do nothing
    #         raise err
    #     # print("Email:", credentialDictGet_email(credentialDICT))
    #     # print("Email Veffied:", credentialDictGet_emailVerfied(credentialDICT))
    #     # print("known_as:", credentialDictGet_known_as(credentialDICT))
    #
    # # check the auth and if it is not valid raise authFailedException
    # def _auth(self, appObj, obj, credentialDICT):
    #     # not required as auths are checked at the enrichment stage
    #     pass

    def canMakeKeyWithoutEnrichment(self):
        return False