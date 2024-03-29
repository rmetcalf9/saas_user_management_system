#Provides auth provider functions
from .Exceptions import CustomAuthProviderExceptionClass, AuthNotFoundException
from .authProviders_base import InvalidAuthConfigException
from .authProviders_Internal import authProviderInternal
from .authProviders_Google import authProviderGoogle
from .authProviders_Facebook import authProviderFacebook
###from .authProviders_LDAP import authProviderLDAP
from uuid import uuid4
from base64 import b64encode
from .authsCommon import getAuthRecord, SaveAuthRecord, UpdateAuthRecord, DeleteAuthRecord

def authProviderFactory(dataDict, guid, tenantName, tenantObj, appObj):
  if dataDict["Type"]=='internal':
    return authProviderInternal(dataDict, guid, tenantName, tenantObj, appObj)
  if dataDict["Type"]=='google':
    return authProviderGoogle(dataDict, guid, tenantName, tenantObj, appObj)
  if dataDict["Type"]=='facebook':
    return authProviderFacebook(dataDict, guid, tenantName, tenantObj, appObj)
  ###if dataDict["Type"]=='ldap':
  ###  return authProviderLDAP(dataDict, guid, tenantName, tenantObj, appObj)
  raise InvalidAuthConfigException

def _getAuthProviderJSON(appObj, guid, saltForPasswordHashing, menuText, iconLink, Type, AllowUserCreation,
  configJSON, AllowLink, AllowUnlink, LinkText
):
  if not isinstance(configJSON,dict):
    raise Exception('ERROR ConfigJSON must be a dict')
  authProvDataDict = {
    "guid": guid,
    "MenuText": menuText,
    "IconLink": iconLink,
    "Type":  Type,
    "AllowUserCreation": AllowUserCreation,
    "AllowLink": AllowLink,
    "AllowUnlink": AllowUnlink,
    "LinkText": LinkText,
    "ConfigJSON": configJSON,  #Type spercific config
    "saltForPasswordHashing": saltForPasswordHashing,
    "AllowLink": AllowLink,
    "AllowUnlink": AllowUnlink,
    "LinkText": LinkText,
  }
  createdAuthProvObject = authProviderFactory(authProvDataDict, 'invalidGUID', 'invalidTenantName', None, appObj) #Check we can create an auth provider
  return authProvDataDict

def getExistingAuthProviderJSON(appObj, existingJSON, menuText, iconLink, Type, AllowUserCreation, configJSON, AllowLink, AllowUnlink, LinkText):
  return _getAuthProviderJSON(
    appObj,
    existingJSON['guid'],
    existingJSON['saltForPasswordHashing'],
    menuText, iconLink, Type, AllowUserCreation, configJSON, AllowLink, AllowUnlink, LinkText
  )

def getNewAuthProviderJSON(appObj, menuText, iconLink, Type, AllowUserCreation, configJSON, AllowLink, AllowUnlink, LinkText):
  return _getAuthProviderJSON(
    appObj, str(uuid4()), str(b64encode(appObj.bcrypt.gensalt()),'utf-8'),
    menuText, iconLink, Type, AllowUserCreation, configJSON, AllowLink, AllowUnlink, LinkText
  )
