# Code to handle tenant objects
from constants import customExceptionClass, masterTenantName, masterTenantDefaultDescription, masterTenantDefaultAuthProviderMenuText, masterTenantDefaultAuthProviderMenuIconLink, uniqueKeyCombinator, masterTenantDefaultSystemAdminRole, authProviderNotFoundException, PersonHasNoAccessToAnyIdentitiesException, tenantAlreadtExistsException, tenantDosentExistException, ShouldNotSupplySaltWhenCreatingAuthProvException, cantUpdateExistingAuthProvException, cantDeleteMasterTenantException
import uuid
from authProviders import authProviderFactory, getNewAuthProviderJSON, getExistingAuthProviderJSON
from authProviders_Internal import getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse
from tenantObj import tenantClass
import jwt
from persons import CreatePerson
from jwtTokenGeneration import generateJWTToken
from objectStores_base import WrongObjectVersionException
from users import CreateUser, AddUserRole, GetUser, associateUserWithPerson, getListOfUserIDsForPerson

failedToCreateTenantException = Exception('Failed to create Tenant')
UserIdentityWithThisNameAlreadyExistsException = Exception('User Identity With This Name Already Exists')
UserAlreadyAssociatedWithThisIdentityException = Exception('User Already Associated With This Identity')
UnknownIdentityException = Exception('Unknown Identity')
authProviderTypeNotFoundException = customExceptionClass('Auth Provider Type not found', 'authProviderTypeNotFoundException')
userCreationNotAllowedException = customExceptionClass('User Creaiton Not Allowed', 'userCreationNotAllowedException')

#only called on intial setup Creates a master tenant with single internal auth provider
def CreateMasterTenant(appObj):
  print("Creating master tenant")
  _createTenant(appObj, masterTenantName, masterTenantDefaultDescription, False)
  masterTenantInternalAuthProvider = AddAuthProvider(
    appObj, 
    masterTenantName, 
    masterTenantDefaultAuthProviderMenuText, 
    masterTenantDefaultAuthProviderMenuIconLink, 
    "internal", 
    False, 
    {"userSufix": "@internalDataStore"}
  )
  
  userID = appObj.defaultUserGUID
  InternalAuthUsername = appObj.APIAPP_DEFAULTHOMEADMINUSERNAME
  
  #User spercific creation
  CreateUser(appObj, {"user_unique_identifier": userID, "known_as": InternalAuthUsername}, masterTenantName, 'init/CreateMasterTenant')
  AddUserRole(appObj, userID, masterTenantName, masterTenantDefaultSystemAdminRole)
  
  person = CreatePerson(appObj)
  credentialJSON = {
    "username": InternalAuthUsername, 
    "password": getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(
      appObj, InternalAuthUsername, appObj.APIAPP_DEFAULTHOMEADMINPASSWORD, masterTenantInternalAuthProvider['saltForPasswordHashing']
    )
  }

  authData = _getAuthProvider(appObj, masterTenantName, masterTenantInternalAuthProvider['guid']).AddAuth(appObj, credentialJSON, person['guid'])

  #mainUserIdentity with authData
  
  associateUserWithPerson(appObj, userID, person['guid'])


#Called from API call

#returns tenantObj
def CreateTenant(appObj, tenantName, description="", allowUserCreation=False):
  if tenantName == masterTenantName:
    raise failedToCreateTenantException
  return _createTenant(appObj, tenantName, description, allowUserCreation)
  
def UpdateTenant(appObj, tenantName, description, allowUserCreation, authProvDict, objectVersion):
  tenantObj = GetTenant(appObj, tenantName)
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
  
  def updTenant(tenant):
    if tenant is None:
      raise tenantDosentExistException
    return jsonForTenant
  appObj.objectStore.updateJSONObject(appObj,"tenants", tenantName, updTenant, objectVersion)
  return GetTenant(appObj, tenantName)
  
def DeleteTenant(appObj, tenantName, objectVersion):
  if tenantName == masterTenantName:
    raise cantDeleteMasterTenantException
  tenantObj = GetTenant(appObj, tenantName)
  if tenantObj is None:
    raise tenantDosentExistException
  ##print("DeleteTenant objectVersion:", objectVersion)
  appObj.objectStore.removeJSONObject(appObj, "tenants", tenantName, objectVersion)
  return tenantObj

def RegisterUser(appObj, tenantObj, authProvGUID, credentialDICT, createdBy):
  if not tenantObj.getAllowUserCreation():
    raise userCreationNotAllowedException
  authProvObj = _getAuthProvider(appObj, tenantObj.getName(), authProvGUID)
  if not authProvObj.getAllowUserCreation():
    raise userCreationNotAllowedException
  
  userData = authProvObj.getTypicalAuthData(credentialDICT)
  CreateUser(appObj, userData, tenantObj.getName(), createdBy)
  person = CreatePerson(appObj)
  authData = authProvObj.AddAuth(appObj, credentialDICT, person['guid'])
  associateUserWithPerson(appObj, userData['user_unique_identifier'], person['guid'])
  
  return GetUser(appObj, userData['user_unique_identifier'])
  
def AddAuthProvider(appObj, tenantName, menuText, iconLink, Type, AllowUserCreation, configJSON):
  authProviderJSON = getNewAuthProviderJSON(appObj, menuText, iconLink, Type, AllowUserCreation, configJSON)
  def updTenant(tenant):
    if tenant is None:
      raise tenantDosentExistException
    tenant["AuthProviders"][authProviderJSON['guid']] = authProviderJSON
    return tenant
  #This update function will not alter the tenant version at all so we can find the latest object version and use that
  appObj.objectStore.updateJSONObject(appObj,"tenants", tenantName, updTenant, None)
  return authProviderJSON
  
# called locally
def _createTenant(appObj, tenantName, description, allowUserCreation):
  tenantWithSameName, ver, creationDateTime, lastUpdateDateTime =  appObj.objectStore.getObjectJSON(appObj,"tenants", tenantName)
  if tenantWithSameName is not None:
    raise tenantAlreadtExistsException
  jsonForTenant = {
    "Name": tenantName,
    "Description": description,
    "AllowUserCreation": allowUserCreation,
    "AuthProviders": {}
  }
  createdTenantVer = appObj.objectStore.saveJSONObject(appObj,"tenants", tenantName, jsonForTenant, None)
  return tenantClass(jsonForTenant, createdTenantVer)

def GetTenant(appObj, tenantName):
  a, aVer, creationDateTime, lastUpdateDateTime = appObj.objectStore.getObjectJSON(appObj,"tenants",tenantName)
  if a is None:
    return a
  return tenantClass(a, aVer)
  
def _getAuthProvider(appObj, tenantName, authProviderGUID):
  tenant = GetTenant(appObj, tenantName)
  if tenant is None:
    raise tenantDosentExistException
  AuthProvider = authProviderFactory(tenant.getAuthProvider(authProviderGUID),authProviderGUID)
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
def Login(appObj, tenantName, authProviderGUID, credentialJSON, requestedUserID='not_valid_guid'):
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
  authUserObj = _getAuthProvider(appObj, tenantName, authProviderGUID).Auth(appObj, credentialJSON)
  if authUserObj is None:
    raise Exception
  
  #We have authed with a single authMethod, we need to get a list of identities for that provider
  possibleUserIDs = getListOfUserIDsForPerson(appObj, authUserObj['personGUID'], tenantName)
  ###print("tenants.py LOGIN possibleUserIDs:",possibleUserIDs, ":", authUserObj['personGUID'])
  if len(possibleUserIDs)==0:
    raise PersonHasNoAccessToAnyIdentitiesException
  if requestedUserID == "not_valid_guid":
    if len(possibleUserIDs)==1:
      requestedUserID = possibleUserIDs[0]
    else:
      #mutiple userids supplied
      resDict['possibleUserIDs'] = possibleUserIDs
      return resDict
  if requestedUserID not in possibleUserIDs:
    raise UnknownIdentityException

  userDict = GetUser(appObj,requestedUserID).getReadOnlyDict()
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

