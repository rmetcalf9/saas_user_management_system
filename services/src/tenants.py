# Code to handle tenant objects
from constants import customExceptionClass, masterTenantName, masterTenantDefaultDescription, masterTenantDefaultAuthProviderMenuText, masterTenantDefaultAuthProviderMenuIconLink, uniqueKeyCombinator, masterTenantDefaultSystemAdminRole, DefaultHasAccountRole, authProviderNotFoundException, PersonHasNoAccessToAnyIdentitiesException, tenantAlreadtExistsException, tenantDosentExistException, ShouldNotSupplySaltWhenCreatingAuthProvException, cantUpdateExistingAuthProvException, cantDeleteMasterTenantException
import uuid
from authProviders import authProviderFactory, getNewAuthProviderJSON, getExistingAuthProviderJSON
from authProviders_Internal import getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse
from tenantObj import tenantClass
from identityObj import createNewIdentity, associateIdentityWithPerson, getListOfIdentitiesForPerson
import jwt
from person import CreatePerson, associatePersonWithAuth
from jwtTokenGeneration import generateJWTToken

failedToCreateTenantException = Exception('Failed to create Tenant')
UserIdentityWithThisNameAlreadyExistsException = Exception('User Identity With This Name Already Exists')
UserAlreadyAssociatedWithThisIdentityException = Exception('User Already Associated With This Identity')
UnknownIdentityException = Exception('Unknown Identity')
authProviderTypeNotFoundException = customExceptionClass('Auth Provider Type not found', 'authProviderTypeNotFoundException')


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
  CreateUser(appObj, userID, masterTenantName)
  AddUserRole(appObj, userID, masterTenantName, masterTenantDefaultSystemAdminRole)
  mainUserIdentity = createNewIdentity(appObj, 'standard','standard', userID)
  
  person = CreatePerson(appObj)
  authData = AddAuth(appObj, masterTenantName, masterTenantInternalAuthProvider['guid'], {
    "username": InternalAuthUsername, 
    "password": getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(
      appObj, InternalAuthUsername, appObj.APIAPP_DEFAULTHOMEADMINPASSWORD, masterTenantInternalAuthProvider['saltForPasswordHashing']
    )
    },
    person['guid']
  )
  associatePersonWithAuth(appObj, person['guid'], authData['AuthUserKey'])

  #mainUserIdentity with authData
  
  associateIdentityWithPerson(appObj, mainUserIdentity['guid'], person['guid'])



#Called from API call

#returns tenantObj
def CreateTenant(appObj, tenantName, description="", allowUserCreation=False):
  if tenantName == masterTenantName:
    raise failedToCreateTenantException
  return _createTenant(appObj, tenantName, description, allowUserCreation)
  
def UpdateTenant(appObj, tenantName, description, allowUserCreation, authProvDict):
  tenantObj = GetTenant(appObj, tenantName)
  if tenantObj is None:
    raise tenantDosentExistException

  jsonForTenant = {
    "Name": tenantName,
    "Description": description,
    "AllowUserCreation": allowUserCreation,
    "AuthProviders": {}
  }
  for authProv in authProvDict:
    newAuthDICT = {}
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
  appObj.objectStore.updateJSONObject(appObj,"tenants", tenantName, updTenant)
  return GetTenant(appObj, tenantName)
  
def DeleteTenant(appObj, tenantName):
  if tenantName == masterTenantName:
    raise cantDeleteMasterTenantException
  tenantObj = GetTenant(appObj, tenantName)
  if tenantObj is None:
    raise tenantDosentExistException
  appObj.objectStore.removeJSONObject(appObj, "tenants", tenantName)
  return tenantObj
  
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
  tenantWithSameName, ver =  appObj.objectStore.getObjectJSON(appObj,"tenants", tenantName)
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
  a, aVer = appObj.objectStore.getObjectJSON(appObj,"tenants",tenantName)
  if a is None:
    return a
  return tenantClass(a, aVer)
  
def CreateUser(appObj, UserID, mainTenant):
  appObj.objectStore.saveJSONObject(appObj,"users", UserID, {
    "UserID": UserID,
    "TenantRoles": {}
  })
  AddUserRole(appObj, UserID, mainTenant, DefaultHasAccountRole)


def AddUserRole(appObj, userID, tennantName, roleName):
  def updUser(obj):
    if obj is None:
      raise userNotFoundException
    if tennantName not in obj["TenantRoles"]:
      obj["TenantRoles"][tennantName] = [roleName]
    else:
      obj["TenantRoles"][tennantName].append(roleName)
    return obj
  appObj.objectStore.updateJSONObject(appObj,"users", userID, updUser)


def _getAuthProvider(appObj, tenantName, authProviderGUID):
  tenant = GetTenant(appObj, tenantName)
  if tenant is None:
    raise tenantDosentExistException
  AuthProvider = authProviderFactory(tenant.getAuthProvider(authProviderGUID)["Type"],tenant.getAuthProvider(authProviderGUID)["ConfigJSON"],authProviderGUID)
  if AuthProvider is None:
    print("Can't find auth provider with type \"" + tenant.getAuthProvider(authProviderGUID)["Type"] + "\" for tenant " + tenant.getName())
    raise authProviderTypeNotFoundException
  return AuthProvider
    
def AddAuth(appObj, tenantName, authProviderGUID, StoredUserInfoJSON, personGUID):
  auth = _getAuthProvider(appObj, tenantName, authProviderGUID).AddAuth(appObj, StoredUserInfoJSON, personGUID)
  return auth
  
# Login function will
# - raise an exception if auth fails
# - raise an exception is user identityGUID is missing or not allowed for this object
# - if no identityGUID is specified and the user only has one identity then the user and role info for the selected identity is returned
# - if no identityGUID is specified and the user has mutiple identities a list of possible identities is returned
# - if an identityGUID is specified and correct then the user and role info
def Login(appObj, tenantName, authProviderGUID, credentialJSON, identityGUID='not_valid_guid'):
  resDict = {
    'possibleIdentities': None,
    'jwtData': None,
    'refresh': None,
    'userGuid': None,
    'authedPersonGuid': None
  }
  authUserObj = _getAuthProvider(appObj, tenantName, authProviderGUID).Auth(appObj, credentialJSON)
  if authUserObj is None:
    raise Exception
  
  #We have authed with a single authMethod, we need to get a list of identities for that provider
  possibleIdentities = getListOfIdentitiesForPerson(appObj, authUserObj['personGUID'])
  if len(possibleIdentities)==0:
    raise PersonHasNoAccessToAnyIdentitiesException
  if identityGUID == "not_valid_guid":
    if len(possibleIdentities)==1:
      for key in possibleIdentities.keys():
        identityGUID = key
    else:
      resDict['possibleIdentities'] = possibleIdentities
      return resDict
  if identityGUID not in possibleIdentities:
    raise UnknownIdentityException
  if possibleIdentities[identityGUID] is None:
    raise Exception
    

  userDict, userDictVer = appObj.objectStore.getObjectJSON(appObj,"users",possibleIdentities[identityGUID]['userID'])
  if userDict is None:
    raise Exception('Error userID found in identity was never created')

  jwtSecretAndKey = appObj.gateway.CheckUserInitAndReturnJWTSecretAndKey(userDict['UserID'])
  resDict['userGuid'] = userDict['UserID']
  resDict['authedPersonGuid'] = authUserObj['personGUID']
  
  tokenWithoutJWTorRefresh = {
    'possibleIdentities': resDict['possibleIdentities'],
    'userGuid': resDict['userGuid'],
    'authedPersonGuid': resDict['authedPersonGuid']
  }

  resDict['jwtData'] = generateJWTToken(appObj, userDict, jwtSecretAndKey, authUserObj['personGUID'])
  resDict['refresh'] = appObj.refreshTokenManager.generateRefreshTokenFirstTime(appObj, tokenWithoutJWTorRefresh, userDict, jwtSecretAndKey, authUserObj['personGUID'])

  return resDict

