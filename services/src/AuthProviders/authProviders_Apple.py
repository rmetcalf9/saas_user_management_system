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
def credentialDictGet_email(credentialDICT):
  return credentialDICT["enriched"]["decodedjwt"].get("email", "")
def credentialDictGet_email_verified(credentialDICT):
    value = credentialDICT["enriched"]["decodedjwt"].get("email_verified", False)
    if isinstance(value, str):
        return value.lower() == "true"
    return bool(value)
def credentialDictGet_is_private_email(credentialDICT):
  return credentialDICT["enriched"]["decodedjwt"].get("is_private_email", "")

def decodeAppleJwtToken(identityToken, clientId, authProviders_AppleJwtPubKeyCache):
    header = jwt.get_unverified_header(identityToken)
    if "kid" not in header:
        raise Exception("KID not found in JWT token")

    appleKey = authProviders_AppleJwtPubKeyCache.getKey(header["kid"])

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
    def _getTypicalAuthData(self, credentialDICT):
        known_as = credentialDictGet_email(credentialDICT)
        if "user" in credentialDICT:
            try:
                known_as = credentialDICT["user"]["name"]["firstName"]
            except KeyError:
                pass

        retVal = {
            "user_unique_identifier": str(uuid.uuid4()),
            "known_as": known_as,  # used to display in UI for the user name
            "other_data": {
                "email": credentialDictGet_email(credentialDICT),
                "email_verified": credentialDictGet_email_verified(credentialDICT),
                "is_private_email": credentialDictGet_is_private_email(credentialDICT)
            }  # Other data like name full name that can be provided - will vary between auth providers
        }
        if "user" in credentialDICT:
            retVal["other_data"]["user"] = credentialDICT["user"]
        return retVal

    def _getAuthData(self, appObj, credentialDICT):
        retVal = {
            "email": credentialDictGet_email(credentialDICT),
            "email_verified": credentialDictGet_email_verified(credentialDICT),
            "is_private_email": credentialDictGet_is_private_email(credentialDICT)
        }
        if "user" in credentialDICT:
            retVal["user"] = credentialDICT["user"]
        return retVal

    def __init__(self, dataDict, guid, tenantName, tenantObj, appObj):
        super().__init__(dataDict, guid, tenantName, tenantObj, appObj)
        if 'service_id' not in dataDict['ConfigJSON']:
            print("Missing service ID")
            raise InvalidAuthConfigException
        if dataDict['ConfigJSON']['service_id'] == "":
            print("Empty service ID")
            raise InvalidAuthConfigException

        if not isinstance(dataDict['ConfigJSON']['service_id'], str):
            print("Service ID not string")
            raise InvalidAuthConfigException

        # Only load the static data once
        if not self.hasStaticData():
            # print('Static data not present loading')
            staticDataValue = {
            }
            self.setStaticData(staticDataValue)

    def _makeKey(self, credentialDICT):
        if 'identityToken' not in credentialDICT:
            print("Missing identity token")
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
                "decodedjwt": decodeAppleJwtToken(identityToken=credentialDICT["identityToken"], clientId=self.__getClientID(), authProviders_AppleJwtPubKeyCache=appObj.authProviders_AppleJwtPubKeyCache)
            }
            return retVal
        except Exception as err:
            # print(err)  # for the repr
            # print(str(err))  # for just the message
            # print(err.args)  # the arguments that the exception has been called with.
            raise constants.authFailedException

    def _AuthActionToTakeWhenThereIsNoRecord(self, credentialDICT, storeConnection, ticketObj, ticketTypeObj):
        try:
            # RegisterUser checks for allowusercreation
            self.appObj.RegisterUserFn(self.tenantObj, self.guid, credentialDICT,
                                       "authProviders_Apple/_AuthActionToTakeWhenThereIsNoRecord", storeConnection,
                                       ticketObj, ticketTypeObj)
        except constants.customExceptionClass as err:
            if err.id == 'userCreationNotAllowedException':
                return  # Do nothing
            raise err

    # check the auth and if it is not valid raise authFailedException
    def _auth(self, appObj, obj, credentialDICT):
        # not required as auths are checked at the enrichment stage
        pass

    def canMakeKeyWithoutEnrichment(self):
        return False