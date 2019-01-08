# File to hold constants

masterTenantName="usersystem"
masterTenantDefaultDescription="Master Tenant for User Management System"
masterTenantDefaultAuthProviderMenuText="Website account login"
masterTenantDefaultAuthProviderMenuIconLink=None
masterTenantDefaultSystemAdminRole="systemadmin"
DefaultHasAccountRole="hasaccount"

uniqueKeyCombinator="_`@\/'"

masterInternalAuthTypePassword="dsF4F.D32654.....3D5g"

class authProviderNotFoundException(Exception):
  pass

class authFailedException(Exception):
  pass