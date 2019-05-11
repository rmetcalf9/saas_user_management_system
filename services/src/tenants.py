# Code to handle tenant objects
from constants import customExceptionClass, masterTenantName, masterTenantDefaultDescription, masterTenantDefaultAuthProviderMenuText, masterTenantDefaultAuthProviderMenuIconLink, uniqueKeyCombinator, masterTenantDefaultSystemAdminRole, authProviderNotFoundException, PersonHasNoAccessToAnyIdentitiesException, tenantAlreadtExistsException, tenantDosentExistException, ShouldNotSupplySaltWhenCreatingAuthProvException, cantUpdateExistingAuthProvException, cantDeleteMasterTenantException, personDosentExistException, userCreationNotAllowedException
import constants
import uuid
from authProviders import authProviderFactory, getNewAuthProviderJSON, getExistingAuthProviderJSON
from authProviders_Internal import getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse
from tenantObj import tenantClass
import jwt
from persons import CreatePerson
from jwtTokenGeneration import generateJWTToken
from object_store_abstraction import WrongObjectVersionException
from users import CreateUser, AddUserRole, associateUserWithPerson
from userPersonCommon import getListOfUserIDsForPerson, GetUser, getListOfUserIDsForPersonNoTenantCheck
from persons import GetPerson

failedToCreateTenantException = Exception('Failed to create Tenant')
UserIdentityWithThisNameAlreadyExistsException = Exception('User Identity With This Name Already Exists')
UserAlreadyAssociatedWithThisIdentityException = Exception('User Already Associated With This Identity')
UnknownUserIDException = customExceptionClass('Unknown UserID', 'UnknownUserIDException')
authProviderTypeNotFoundException = customExceptionClass('Auth Provider Type not found', 'authProviderTypeNotFoundException')

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
    storeConnection,
    False, False, 'Unlink'
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
  AddUserRole(appObj, userID, masterTenantName, constants.masterTenantDefaultSystemAdminRole, storeConnection)
  AddUserRole(appObj, userID, masterTenantName, constants.SecurityEndpointAccessRole, storeConnection)

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
    storeConnection,
    None
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
      #No defaults provided
      newAuthDICT = getExistingAuthProviderJSON(
        appObj, existingAuthProv, authProv['MenuText'], authProv['IconLink'], authProv['Type'], 
        authProv['AllowUserCreation'], authProv['ConfigJSON'],
        authProv['AllowLink'], authProv['AllowUnlink'], authProv['UnlinkText']
      )
    else:
      if authProv['saltForPasswordHashing'] is not None:
        raise ShouldNotSupplySaltWhenCreatingAuthProvException
      newAuthDICT = getNewAuthProviderJSON(
        appObj, authProv['MenuText'], authProv['IconLink'], authProv['Type'], 
        authProv['AllowUserCreation'], authProv['ConfigJSON'],
        authProv.get('AllowLink',False), authProv.get('AllowUnlink',False), authProv.get('UnlinkText','Unlink')
      )
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
  tenantObj = GetTenant(tenantName, storeConnection, 'a','b','c')
  if tenantObj is None:
    raise tenantDosentExistException
  ##print("DeleteTenant objectVersion:", objectVersion)
  storeConnection.removeJSONObject("tenants", tenantName, objectVersion)
  return tenantObj

def RegisterUser(appObj, tenantObj, authProvGUID, credentialDICT, createdBy, storeConnection):
  if not tenantObj.getAllowUserCreation():
    raise userCreationNotAllowedException
  authProvObj = _getAuthProvider(appObj, tenantObj.getName(), authProvGUID, storeConnection, tenantObj)
  if not authProvObj.getAllowUserCreation():
    raise userCreationNotAllowedException
  
  userData = authProvObj.getTypicalAuthData(credentialDICT)
  CreateUser(appObj, userData, tenantObj.getName(), createdBy, storeConnection)
  person = CreatePerson(appObj, storeConnection, None, 'a','b','c')
  authData = authProvObj.AddAuth(appObj, credentialDICT, person['guid'], storeConnection)
  associateUserWithPerson(appObj, userData['user_unique_identifier'], person['guid'], storeConnection)
  
  return GetUser(appObj, userData['user_unique_identifier'], storeConnection)

def ExecuteAuthOperation(appObj, credentialDICT, storeConnection, operationName, operationDICT, tenantName, authProvGUID):
  tenantObj = GetTenant(tenantName, storeConnection, 'a','b','c')
  if tenantObj is None:
    raise tenantDosentExistException
  authProvObj = _getAuthProvider(appObj, tenantObj.getName(), authProvGUID, storeConnection, tenantObj)
  authProvObj.executeAuthOperation(appObj, credentialDICT, storeConnection, operationName, operationDICT)

def AddAuthForUser(appObj, tenantName, authProvGUID, personGUID, credentialDICT, storeConnection):
  tenantObj = GetTenant(tenantName, storeConnection, 'a','b','c')
  if tenantObj is None:
    raise tenantDosentExistException
  personObj = GetPerson(appObj, personGUID, storeConnection)
  if personObj is None:
    raise personDosentExistException
  authProvObj = _getAuthProvider(appObj, tenantObj.getName(), authProvGUID, storeConnection, tenantObj)
  authData = authProvObj.AddAuth(appObj, credentialDICT, personGUID, storeConnection)
  
  return authData


def AddAuthProvider(appObj, tenantName, menuText, iconLink, Type, AllowUserCreation, configJSON, storeConnection, AllowLink, AllowUnlink, UnlinkText):
  authProviderJSON = getNewAuthProviderJSON(appObj, menuText, iconLink, Type, AllowUserCreation, configJSON, AllowLink, AllowUnlink, UnlinkText)
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
  for curAuthProv in a['AuthProviders']:
    if not 'AllowLink' in a['AuthProviders'][curAuthProv]:
      a['AuthProviders'][curAuthProv]['AllowLink'] = False
    if not 'AllowUnlink' in a['AuthProviders'][curAuthProv]:
      a['AuthProviders'][curAuthProv]['AllowUnlink'] = False
    if not 'UnlinkText' in a['AuthProviders'][curAuthProv]:
      a['AuthProviders'][curAuthProv]['UnlinkText'] = 'Unlink ' + a['AuthProviders'][curAuthProv]['Type']
  return tenantClass(a, aVer)
  
def _getAuthProvider(appObj, tenantName, authProviderGUID, storeConnection, tenantObj):
  if tenantObj is None:
    tenantObj = GetTenant(tenantName, storeConnection, 'a', 'b', 'c')
    if tenantObj is None:
      raise tenantDosentExistException
  AuthProvider = authProviderFactory(tenantObj.getAuthProvider(authProviderGUID),authProviderGUID, tenantName, tenantObj, appObj)
  if AuthProvider is None:
    print("Can't find auth provider with type \"" + tenantObj.getAuthProvider(authProviderGUID)["Type"] + "\" for tenant " + tenantObj.getName())
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
  tenantObj = GetTenant(tenantName, storeConnection, 'a', 'b', 'c')
  if tenantObj is None:
    raise tenantDosentExistException

  authProvider = _getAuthProvider(appObj, tenantName, authProviderGUID, storeConnection, tenantObj)
  authUserObj = authProvider.Auth(appObj, credentialJSON, storeConnection)
  if authUserObj is None:
    raise Exception
  
  #We have authed with a single authMethod, we need to get a list of identities for that provider
  possibleUserIDs = getListOfUserIDsForPerson(appObj, authUserObj['personGUID'], tenantName, GetUser, storeConnection)
  ###print("tenants.py LOGIN possibleUserIDs:",possibleUserIDs, ":", authUserObj['personGUID'])
  if len(possibleUserIDs)==0:
    if not tenantObj.getAllowUserCreation():
      raise PersonHasNoAccessToAnyIdentitiesException
    if not authProvider.getAllowUserCreation():
      raise PersonHasNoAccessToAnyIdentitiesException
    if authProvider.requireRegisterCallToAutocreateUser():
      raise PersonHasNoAccessToAnyIdentitiesException
    #print("No possible identities returned - this means there is no has account role - we should add it")
    
    #Person may have many users, but if we can create accounts for this tenant we can add the account to all users
    # and give the person logging in a choice
    #We don't do a tenant check because all it's doing is restricting the returned users to users who already have a hasaccount role
    userIDList = getListOfUserIDsForPersonNoTenantCheck(appObj, authUserObj['personGUID'], storeConnection)
    for curUserID in userIDList:
      AddUserRole(appObj, curUserID, tenantName, constants.DefaultHasAccountRole, storeConnection)
    
    possibleUserIDs = getListOfUserIDsForPerson(appObj, authUserObj['personGUID'], tenantName, GetUser, storeConnection)
    if len(possibleUserIDs)==0:
      #This should never happen as we just added the has account role
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
  resDict['jwtData'] = generateJWTToken(appObj, userDict, appObj.APIAPP_JWTSECRET, userDict['UserID'], authUserObj['personGUID'])
  resDict['refresh'] = appObj.refreshTokenManager.generateRefreshTokenFirstTime(appObj, tokenWithoutJWTorRefresh, userDict, userDict['UserID'], authUserObj['personGUID'])

  return resDict

