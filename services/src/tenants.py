# Code to handle tenant objects
from constants import masterTenantName, masterTenantDefaultDescription

failedToCreateTenantException = Exception('Failed to create Tenant')

#only called on intial setup Creates a master tenant with single internal auth provider
def CreateMasterTenant(appObj):
  _createTenant(appObj, masterTenantName, masterTenantDefaultDescription, False)

#Called from API call
def CreateTenant(appObj, tenantName):
  if tenantName == masterTenantName:
    raise failedToCreateTenantException
  _createTenant(appObj, tenantName)
  
# called locally
def _createTenant(appObj, tenantName, description, allowUserCreation):
  appObj.objectStore.saveJSONObject(appObj,tenantName, {
    "Name": tenantName,
    "Description": description,
    "AllowUserCreation": allowUserCreation
  })

def GetTenant(appObj, tenantName):
  return appObj.objectStore.getObjectJSON(appObj,tenantName)