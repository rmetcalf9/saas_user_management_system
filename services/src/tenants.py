# Code to handle tenant objects
from constants import customExceptionClass, masterTenantName, masterTenantDefaultDescription, masterTenantDefaultAuthProviderMenuText, masterTenantDefaultAuthProviderMenuIconLink, uniqueKeyCombinator, masterTenantDefaultSystemAdminRole, authProviderNotFoundException, PersonHasNoAccessToAnyIdentitiesException, tenantAlreadtExistsException, tenantDosentExistException, ShouldNotSupplySaltWhenCreatingAuthProvException, cantUpdateExistingAuthProvException, cantDeleteMasterTenantException, personDosentExistException
import uuid
from authProviders import authProviderFactory, getNewAuthProviderJSON, getExistingAuthProviderJSON
from authProviders_Internal import getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse
from tenantObj import tenantClass
import jwt
from persons import CreatePerson
from jwtTokenGeneration import generateJWTToken
from objectStores_base import WrongObjectVersionException
from users import CreateUser, AddUserRole, associateUserWithPerson
from userPersonCommon import getListOfUserIDsForPerson, GetUser
from persons import GetPerson

failedToCreateTenantException = Exception('Failed to create Tenant')
UserIdentityWithThisNameAlreadyExistsException = Exception('User Identity With This Name Already Exists')
UserAlreadyAssociatedWithThisIdentityException = Exception('User Already Associated With This Identity')
UnknownUserIDException = customExceptionClass('Unknown UserID', 'UnknownUserIDException')
authProviderTypeNotFoundException = customExceptionClass('Auth Provider Type not found', 'authProviderTypeNotFoundException')
userCreationNotAllowedException = customExceptionClass('User Creaiton Not Allowed', 'userCreationNotAllowedException')

#only called on intial setup Creates a master tenant with single internal auth provider
def CreateMasterTenant(appObj, testingMode, storeConnection):
  print("Creating master tenant")
  _createTenant(appObj, masterTenantName, masterTenantDefaultDescription, False, storeConnection)
  masterTenantInternalAuthProvider = AddAuthProvider(
    appObj, 
    masterTenantName, 
    masterTenantDefaultAuthProviderMenuText, 
    masterTenantDefaultAuthProviderMenuIconLink, 
    "internal", 
    False, 
    {"userSufix": "@internalDataStore"},
    storeConnection
  )
  
  userID = appObj.defaultUserGUID
  InternalAuthUsername = appObj.APIAPP_DEFAULTHOMEADMINUSERNAME
  
  #User spercific creation
  CreateUser(
    appObj, 
    {"user_unique_identifier": userID, "known_as": InternalAuthUsername}, 
    masterTenantName, 
    'init/CreateMasterTenant', 
    storeConnection
  )
  AddUserRole(appObj, userID, masterTenantName, masterTenantDefaultSystemAdminRole, storeConnection)

  person = None
  if testingMode:
    person = CreatePerson(appObj, storeConnection, appObj.testingDefaultPersonGUID, 'a','b','c')
  else:
    person = CreatePerson(appObj, storeConnection, None, 'a','b','c')

  credentialJSON = {
    "username": InternalAuthUsername, 
    "password": getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(
      appObj, InternalAuthUsername, appObj.APIAPP_DEFAULTHOMEADMINPASSWORD, masterTenantInternalAuthProvider['saltForPasswordHashing']
    )
  }

  authData = _getAuthProvider(
    appObj, masterTenantName, 
    masterTenantInternalAuthProvider['guid'],
    storeConnection
  ).AddAuth(appObj, credentialJSON, person['guid'], storeConnection)

  #mainUserIdentity with authData
  
  associateUserWithPerson(appObj, userID, person['guid'], storeConnection)


#Called from API call

#returns tenantObj
##allowUserCreation used to default to false, description used to default to ""
def CreateTenant(appObj, tenantName, description, allowUserCreation, storeConnection, a,b,c):
  if tenantName == masterTenantName:
    raise failedToCreateTenantException
  return _createTenant(appObj, tenantName, description, allowUserCreation, storeConnection)
  
def UpdateTenant(appObj, tenantName, description, allowUserCreation, authProvDict, objectVersion, storeConnection):
  tenantObj = GetTenant(tenantName, storeConnection, 'a','b','c')
  if tenantObj is None:
    raise tenantDosentExistException
  if str(tenantObj.getObjectVersion()) != str(objectVersion):
    raise WrongObjectVersionException

  jsonForTenant = {
    "Name": tenantName,
    "Description": description,
    "AllowUserCreation": allowUserCreation,
    "AuthProviders": {}
  }
  for authProv in authProvDict:
    newAuthDICT = {}
    
    if 'saltForPasswordHashing' not in authProv:
      authProv['saltForPasswordHashing'] = None
    if 'guid' not in authProv:
      authProv['guid'] = None
    
    #Accept guid and saltForPasswordHashing as empty string as well as none - both mean a new auth provider needs to be created
    if authProv['guid'] is not None:
      if authProv['guid'] == '':
        authProv['guid'] = None
    if authProv['saltForPasswordHashing'] is not None:
      if authProv['saltForPasswordHashing'] == '':
        authProv['saltForPasswordHashing'] = None

    #If we are updating an existing auth provider the salt for password hashing must be provided
    # and it must match the existing value!
    if authProv['guid'] is not None:
      if authProv['saltForPasswordHashing'] is None:
        raise cantUpdateExistingAuthProvException
      existingAuthProv = tenantObj.getAuthProvider(authProv['guid'])
      if authProv['saltForPasswordHashing'] != existingAuthProv['saltForPasswordHashing']:
        raise cantUpdateExistingAuthProvException
      #print("UpdateTenant:authProb'congigJSON':",authProv['ConfigJSON']," - ", type(authProv['ConfigJSON']))
      newAuthDICT = getExistingAuthProviderJSON(appObj, existingAuthProv, authProv['MenuText'], authProv['IconLink'], authProv['Type'], authProv['AllowUserCreation'], authProv['ConfigJSON'])
    else:
      if authProv['saltForPasswordHashing'] is not None:
        raise ShouldNotSupplySaltWhenCreatingAuthProvException
      newAuthDICT = getNewAuthProviderJSON(appObj, authProv['MenuText'], authProv['IconLink'], authProv['Type'], authProv['AllowUserCreation'], authProv['ConfigJSON'])
    jsonForTenant['AuthProviders'][newAuthDICT['guid']] = newAuthDICT
  
  def updTenant(tenant, storeConnection):
    if tenant is None:
      raise tenantDosentExistException
    return jsonForTenant
  storeConnection.updateJSONObject("tenants", tenantName, updTenant, objectVersion)
  return GetTenant(tenantName, storeConnection, 'a','b','c')
  
def DeleteTenant(appObj, tenantName, objectVersion, storeConnection):
  if tenantName == masterTenantName:
    raise cantDeleteMasterTenantException
  tenantObj = GetTenant(appObj, tenantName)
  if tenantObj is None:
    raise tenantDosentExistException
  ##print("DeleteTenant objectVersion:", objectVersion)
  appObj.objectStore.removeJSONObject(appObj, "tenants", tenantName, objectVersion)
  return tenantObj

def RegisterUser(appObj, tenantObj, authProvGUID, credentialDICT, createdBy, storeConnection):
  if not tenantObj.getAllowUserCreation():
    raise userCreationNotAllowedException
  authProvObj = _getAuthProvider(appObj, tenantObj.getName(), authProvGUID, storeConnection)
  if not authProvObj.getAllowUserCreation():
    raise userCreationNotAllowedException
  
  userData = authProvObj.getTypicalAuthData(credentialDICT)
  CreateUser(appObj, userData, tenantObj.getName(), createdBy, storeConnection)
  person = CreatePerson(appObj, storeConnection, None, 'a','b','c')
  authData = authProvObj.AddAuth(appObj, credentialDICT, person['guid'], storeConnection)
  associateUserWithPerson(appObj, userData['user_unique_identifier'], person['guid'], storeConnection)
  
  return GetUser(appObj, userData['user_unique_identifier'], storeConnection)

def AddAuthForUser(appObj, tenantName, authProvGUID, personGUID, credentialDICT, storeConnection):
  tenantObj = GetTenant(appObj, tenantName)
  if tenantObj is None:
    raise tenantDosentExistException
  personObj = GetPerson(appObj, personGUID)
  if personObj is None:
    raise personDosentExistException
  authProvObj = _getAuthProvider(appObj, tenantObj.getName(), authProvGUID)
  authData = authProvObj.AddAuth(appObj, credentialDICT, personGUID)
  
  return authData


def AddAuthProvider(appObj, tenantName, menuText, iconLink, Type, AllowUserCreation, configJSON, storeConnection):
  authProviderJSON = getNewAuthProviderJSON(appObj, menuText, iconLink, Type, AllowUserCreation, configJSON)
  def updTenant(tenant, transactionContext):
    if tenant is None:
      raise tenantDosentExistException
    tenant["AuthProviders"][authProviderJSON['guid']] = authProviderJSON
    return tenant
  #This update function will not alter the tenant version at all so we can find the latest object version and use that
  storeConnection.updateJSONObject("tenants", tenantName, updTenant)
  return authProviderJSON
  
# called locally
def _createTenant(appObj, tenantName, description, allowUserCreation, storeConnection):
  tenantWithSameName, ver, creationDateTime, lastUpdateDateTime =  storeConnection.getObjectJSON("tenants", tenantName)
  if tenantWithSameName is not None:
    raise tenantAlreadtExistsException
  jsonForTenant = {
    "Name": tenantName,
    "Description": description,
    "AllowUserCreation": allowUserCreation,
    "AuthProviders": {}
  }
  createdTenantVer = storeConnection.saveJSONObject("tenants", tenantName, jsonForTenant)

  return tenantClass(jsonForTenant, createdTenantVer)

def GetTenant(tenantName, storeConnection, a,b,c):
  a, aVer, creationDateTime, lastUpdateDateTime = storeConnection.getObjectJSON("tenants",tenantName)
  if a is None:
    return a
  return tenantClass(a, aVer)
  
def _getAuthProvider(appObj, tenantName, authProviderGUID, storeConnection):
  tenant = GetTenant(tenantName, storeConnection, 'a', 'b', 'c')
  if tenant is None:
    raise tenantDosentExistException
  AuthProvider = authProviderFactory(tenant.getAuthProvider(authProviderGUID),authProviderGUID, tenantName)
  if AuthProvider is None:
    print("Can't find auth provider with type \"" + tenant.getAuthProvider(authProviderGUID)["Type"] + "\" for tenant " + tenant.getName())
    raise authProviderTypeNotFoundException
  return AuthProvider
  
# Login function will
# - raise an exception if auth fails
# - raise an exception is user identityGUID is missing or not allowed for this object
# - if no identityGUID is specified and the user only has one identity then the user and role info for the selected identity is returned
# - if no identityGUID is specified and the user has mutiple identities a list of possible identities is returned
# - if an identityGUID is specified and correct then the user and role info
### requestedUserID can be None
def Login(appObj, tenantName, authProviderGUID, credentialJSON, requestedUserID, storeConnection, a,b,c):
  resDict = {
    'possibleUserIDs': None,
    'possibleUsers': None, #not filled in here but enriched from possibleUserIDs when user selection is required
    'jwtData': None,
    'refresh': None,
    'userGuid': None,
    'authedPersonGuid': None,
    'ThisTenantRoles': None,
    'known_as': None,
    'other_data': None
  }
  #print("tenants.py Login credentialJSON:",credentialJSON)
  authProvider = _getAuthProvider(appObj, tenantName, authProviderGUID, storeConnection)
  authUserObj = authProvider.Auth(appObj, credentialJSON, storeConnection)
  if authUserObj is None:
    raise Exception
  
  #We have authed with a single authMethod, we need to get a list of identities for that provider
  possibleUserIDs = getListOfUserIDsForPerson(appObj, authUserObj['personGUID'], tenantName, GetUser, storeConnection)
  ###print("tenants.py LOGIN possibleUserIDs:",possibleUserIDs, ":", authUserObj['personGUID'])
  if len(possibleUserIDs)==0:
    raise PersonHasNoAccessToAnyIdentitiesException
  if requestedUserID is None:
    if len(possibleUserIDs)==1:
      requestedUserID = possibleUserIDs[0]
    else:
      #mutiple userids supplied
      resDict['possibleUserIDs'] = possibleUserIDs
      return resDict
  if requestedUserID not in possibleUserIDs:
    print('requestedUserID:',requestedUserID)
    raise UnknownUserIDException

  userDict = GetUser(appObj,requestedUserID, storeConnection).getReadOnlyDict()
  if userDict is None:
    raise Exception('Error userID found in identity was never created')

    
  thisTenantRoles = []
  if tenantName in userDict["TenantRoles"]:
    #thisTenantRoles = copy.deepcopy(userDict["TenantRoles"][tenantName])
    for x in userDict["TenantRoles"][tenantName]:
      thisTenantRoles.append(x)

  jwtSecretAndKey = appObj.gateway.CheckUserInitAndReturnJWTSecretAndKey(userDict['UserID'])
  resDict['userGuid'] = userDict['UserID']
  resDict['authedPersonGuid'] = authUserObj['personGUID']
  resDict['ThisTenantRoles'] = thisTenantRoles #Only roles valid for the current tenant are returned
  resDict['known_as'] = userDict["known_as"]
  resDict['other_data'] = userDict["other_data"]

  #This object is stored with the refresh token and the same value is always returned on each refresh
  tokenWithoutJWTorRefresh = {
    'possibleUserIDs': None, #was resDict['possibleUserIDs'], but this will always be none
    'userGuid': resDict['userGuid'],
    'authedPersonGuid': resDict['authedPersonGuid'],
    "ThisTenantRoles": resDict['ThisTenantRoles'],
    "known_as":  resDict['known_as'],
    "other_data":  resDict['other_data']
  }

  #These two sections are rebuilt every refresh
  resDict['jwtData'] = generateJWTToken(appObj, userDict, jwtSecretAndKey, authUserObj['personGUID'])
  resDict['refresh'] = appObj.refreshTokenManager.generateRefreshTokenFirstTime(appObj, tokenWithoutJWTorRefresh, userDict, jwtSecretAndKey, authUserObj['personGUID'])

  return resDict

