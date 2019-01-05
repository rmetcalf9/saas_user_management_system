# Code to handle tenant objects
from constants import masterTenantName, masterTenantDefaultDescription, masterTenantDefaultAuthProviderMenuText, masterTenantDefaultAuthProviderMenuIconLink, uniqueKeyCombinator, masterTenantDefaultSystemAdminRole, DefaultHasAccountRole
import uuid
from authProviders import authProviderFactory

failedToCreateTenantException = Exception('Failed to create Tenant')
tenantNotFoundException = Exception('Tenant Not Found')
authProviderNotFoundException = Exception('Auth Provider Not Found')
authProviderTypeNotFoundException = Exception('Auth Provider Type Not Found')


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
  CreateUser(appObj, appObj.APIAPP_DEFAULTHOMEADMINUSERNAME)
  AddUserRole(appObj, appObj.APIAPP_DEFAULTHOMEADMINUSERNAME, masterTenantName, masterTenantDefaultSystemAdminRole)
  AddUserRole(appObj, appObj.APIAPP_DEFAULTHOMEADMINUSERNAME, masterTenantName, DefaultHasAccountRole)
  AddAuthForUser(appObj, appObj.APIAPP_DEFAULTHOMEADMINUSERNAME, masterTenantName, masterTenantInternalAuthProviderGUID, {
    "username": appObj.APIAPP_DEFAULTHOMEADMINUSERNAME, 
    "password": appObj.APIAPP_DEFAULTHOMEADMINPASSWORD
  })

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
  return appObj.objectStore.getObjectJSON(appObj,"tenants",tenantName)
  
def CreateUser(appObj, UserID):
  appObj.objectStore.saveJSONObject(appObj,"users", UserID, {
    "UserID": UserID,
    "TenantRoles": {}
  })

def AddUserRole(appObj, UserID, tennantName, roleName):
  def updUser(obj):
    if obj is None:
      raise userNotFoundException
    if tennantName not in obj["TenantRoles"]:
      obj["TenantRoles"][tennantName] = [roleName]
    else:
      obj["TenantRoles"][tennantName].append(roleName)
    return obj
  appObj.objectStore.updateJSONObject(appObj,"users", UserID, updUser)

def _getAuthProvider(appObj, tenantName, authProviderGUID):
  tenant = GetTenant(appObj, tenantName)
  if tenant is None:
    raise tenantNotFoundException
  if authProviderGUID not in tenant["AuthProviders"]:
    raise authProviderNotFoundException
  AuthProvider = authProviderFactory(tenant["AuthProviders"][authProviderGUID]["Type"],tenant["AuthProviders"][authProviderGUID]["ConfigJSON"])
  if AuthProvider is None:
    print("Can't find " + tenant["AuthProviders"][authProviderGUID]["Type"])
    raise authProviderTypeNotFoundException
  return AuthProvider
    
def AddAuthForUser(appObj, UserID, tenantName, authProviderGUID, StoredUserInfoJSON):
  _getAuthProvider(appObj, tenantName, authProviderGUID).AddAuthForUser(appObj, UserID, StoredUserInfoJSON)
  
# Login function will return a list of roles
def Login(appObj, tenantName, authProviderGUID, credentialJSON):
  UserID = _getAuthProvider(appObj, tenantName, authProviderGUID).Auth(appObj, credentialJSON)
  UserJSON = appObj.objectStore.getObjectJSON(appObj,"users", UserID)
  if UserJSON is None:
    raise Exception
  return UserJSON


