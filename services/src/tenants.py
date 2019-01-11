# Code to handle tenant objects
from constants import masterTenantName, masterTenantDefaultDescription, masterTenantDefaultAuthProviderMenuText, masterTenantDefaultAuthProviderMenuIconLink, uniqueKeyCombinator, masterTenantDefaultSystemAdminRole, DefaultHasAccountRole, authProviderNotFoundException, PersonHasNoAccessToAnyIdentitiesException
import uuid
from authProviders import authProviderFactory
from tenantObj import tenantClass
from identityObj import createNewIdentity, associateIdentityWithPerson, getListOfIdentitiesForPerson
import jwt
from person import CreatePerson, associatePersonWithAuth
from jwtTokenGeneration import generateJWTToken

failedToCreateTenantException = Exception('Failed to create Tenant')
tenantNotFoundException = Exception('Tenant Not Found')
UserIdentityWithThisNameAlreadyExistsException = Exception('User Identity With This Name Already Exists')
UserAlreadyAssociatedWithThisIdentityException = Exception('User Already Associated With This Identity')
UnknownIdentityException = Exception('Unknown Identity')


#only called on intial setup Creates a master tenant with single internal auth provider
def CreateMasterTenant(appObj):
  print("Creating master tenant")
  _createTenant(appObj, masterTenantName, masterTenantDefaultDescription, False)
  masterTenantInternalAuthProviderGUID = AddAuthProvider(appObj, masterTenantName, {
      "MenuText": masterTenantDefaultAuthProviderMenuText,
      "IconLink": masterTenantDefaultAuthProviderMenuIconLink,
      "Type":  "internal",
      "AllowUserCreation": False,
      "ConfigJSON": {
        "userSufix": "@internalDataStore"
      }
  })
  userID = str(uuid.uuid4())
  InternalAuthUsername = appObj.APIAPP_DEFAULTHOMEADMINUSERNAME
  
  #User spercific creation
  CreateUser(appObj, userID)
  AddUserRole(appObj, userID, masterTenantName, masterTenantDefaultSystemAdminRole)
  AddUserRole(appObj, userID, masterTenantName, DefaultHasAccountRole)
  mainUserIdentity = createNewIdentity(appObj, 'standard','standard', userID)
  
  person = CreatePerson(appObj)
  authData = AddAuth(appObj, masterTenantName, masterTenantInternalAuthProviderGUID, {
    "username": InternalAuthUsername, 
    "password": appObj.APIAPP_DEFAULTHOMEADMINPASSWORD
  },
  person['guid'])
  associatePersonWithAuth(appObj, person['guid'], authData['AuthUserKey'])

  
  #mainUserIdentity with authData
  
  associateIdentityWithPerson(appObj, mainUserIdentity['guid'], person['guid'])



#Called from API call
def CreateTenant(appObj, tenantName):
  if tenantName == masterTenantName:
    raise failedToCreateTenantException
  _createTenant(appObj, tenantName)
  
def AddAuthProvider(appObj, tenantName, authProviderJSON):
  newGUID = str(uuid.uuid4())
  def updTenant(tenant):
    if tenant is None:
      raise tenantNotFoundException
    authProviderJSONLocal = authProviderJSON.copy()
    authProviderJSONLocal['guid'] = newGUID
    tenant["AuthProviders"][authProviderJSONLocal['guid']] = authProviderJSONLocal
    return tenant
  appObj.objectStore.updateJSONObject(appObj,"tenants", tenantName, updTenant)
  return newGUID
  
# called locally
def _createTenant(appObj, tenantName, description, allowUserCreation):
  appObj.objectStore.saveJSONObject(appObj,"tenants", tenantName, {
    "Name": tenantName,
    "Description": description,
    "AllowUserCreation": allowUserCreation,
    "AuthProviders": {}
  })

def GetTenant(appObj, tenantName):
  a = appObj.objectStore.getObjectJSON(appObj,"tenants",tenantName)
  if a is None:
    return a
  return tenantClass(a)
  
def CreateUser(appObj, UserID):
  appObj.objectStore.saveJSONObject(appObj,"users", UserID, {
    "UserID": UserID,
    "TenantRoles": {}
  })

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
    raise tenantNotFoundException
  AuthProvider = authProviderFactory(tenant.getAuthProvider(authProviderGUID)["Type"],tenant.getAuthProvider(authProviderGUID)["ConfigJSON"])
  if AuthProvider is None:
    print("Can't find " + tenant["AuthProviders"][authProviderGUID]["Type"])
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
    'jwtData': None
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
    

  userDict = appObj.objectStore.getObjectJSON(appObj,"users",possibleIdentities[identityGUID]['userID'])
  if userDict is None:
    raise Exception('Error userID found in identity was never created')

  jwtSecretAndKey = appObj.gateway.CheckUserInitAndReturnJWTSecretAndKey(userDict)
  resDict['jwtData'] = generateJWTToken(appObj.APIAPP_JWT_TOKEN_TIMEOUT, userDict, jwtSecretAndKey)
  return resDict

