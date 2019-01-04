# Code to handle tenant objects
from constants import masterTenantName, masterTenantDefaultDescription, masterTenantDefaultAuthProviderMenuText, masterTenantDefaultAuthProviderMenuIconLink
import uuid

failedToCreateTenantException = Exception('Failed to create Tenant')
tenantNotFoundException = Exception('Tenant Not Found')

#only called on intial setup Creates a master tenant with single internal auth provider
def CreateMasterTenant(appObj):
  print("Creating master tenant")
  _createTenant(appObj, masterTenantName, masterTenantDefaultDescription, False)
  AddAuthProvider(appObj, masterTenantName, {
      "guid": str(uuid.uuid4()),
      "MenuText": masterTenantDefaultAuthProviderMenuText,
      "IconLink": masterTenantDefaultAuthProviderMenuIconLink,
      "Type":  "Internal",
      "AllowUserCreation": False,
      "ConfigJSON": {
        "PasswordStoreObjectType": "internalDataStore"
      }
  })

#Called from API call
def CreateTenant(appObj, tenantName):
  if tenantName == masterTenantName:
    raise failedToCreateTenantException
  _createTenant(appObj, tenantName)
  
def AddAuthProvider(appObj, tenantName, authProviderJSON):
  #TODO Auth providers need to be dedicated classes with a class factory

  tenant = GetTenant(appObj, tenantName)
  if tenant is None:
    raise tenantNotFoundException
  tenant["AuthProviders"].append(authProviderJSON)
  appObj.objectStore.saveJSONObject(appObj,"tenants", tenantName, tenant)  
  
# called locally
def _createTenant(appObj, tenantName, description, allowUserCreation):
  appObj.objectStore.saveJSONObject(appObj,"tenants", tenantName, {
    "Name": tenantName,
    "Description": description,
    "AllowUserCreation": allowUserCreation,
    "AuthProviders": []
  })

def GetTenant(appObj, tenantName):
  return appObj.objectStore.getObjectJSON(appObj,"tenants",tenantName)