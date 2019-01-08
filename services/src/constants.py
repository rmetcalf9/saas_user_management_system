# File to hold constants

masterTenantName="usersystem"
masterTenantDefaultDescription="Master Tenant for User Management System"
masterTenantDefaultAuthProviderMenuText="Website account login"
masterTenantDefaultAuthProviderMenuIconLink=None
masterTenantDefaultSystemAdminRole="systemadmin"
DefaultHasAccountRole="hasaccount"

uniqueKeyCombinator="_`@\/'"

masterInternalAuthTypePassword="dsF4F.D32654.....3D5g"

class customExceptionClass(Exception):
  id = None
  text = None
  def __init__(self, text):
    self.id = text
    self.text = text

authProviderNotFoundException = customExceptionClass('authProviderNotFoundException')
authFailedException = customExceptionClass('authFailedException')
