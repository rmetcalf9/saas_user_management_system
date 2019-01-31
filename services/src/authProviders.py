#Provides auth provider functions
from authProviders_Internal import authProviderInternal
from uuid import uuid4
from base64 import b64encode

def authProviderFactory(type, configJSON, guid):
  if type=='internal':
    return authProviderInternal('internal', configJSON, guid)
  return None
  
def _getAuthProviderJSON(appObj, guid, saltForPasswordHashing, menuText, iconLink, Type, AllowUserCreation, configJSON):
  if not isinstance(configJSON,dict):
    raise Exception('ERROR ConfigJSON must be a dict')
  createdAuthProvObject = authProviderFactory(Type, configJSON, 'invalidGUID') #Check we can create an auth provider
  return {
    "guid": guid,
    "MenuText": menuText,
    "IconLink": iconLink,
    "Type":  Type,
    "AllowUserCreation": AllowUserCreation,
    "ConfigJSON": configJSON,
    "saltForPasswordHashing": saltForPasswordHashing
  }

def getExistingAuthProviderJSON(appObj, existingJSON, menuText, iconLink, Type, AllowUserCreation, configJSON):
  createdAuthProvObject = authProviderFactory(Type, configJSON, 'invalidGUID') #Check we can create an auth provider
  return _getAuthProviderJSON(
    appObj, 
    existingJSON['guid'], 
    existingJSON['saltForPasswordHashing'], 
    menuText, iconLink, Type, AllowUserCreation, configJSON
  )

def getNewAuthProviderJSON(appObj, menuText, iconLink, Type, AllowUserCreation, configJSON):
  return _getAuthProviderJSON(
    appObj, str(uuid4()), str(b64encode(appObj.bcrypt.gensalt()),'utf-8'), 
    menuText, iconLink, Type, AllowUserCreation, configJSON
  )

  
