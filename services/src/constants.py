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
  def __init__(self, text, iid=None):
    if iid is None:
      self.id = text
    else:
      self.id = iid
    self.text = text

authProviderNotFoundException = customExceptionClass('authProviderNotFoundException')
authFailedException = customExceptionClass('authFailedException')
PersonHasNoAccessToAnyIdentitiesException = customExceptionClass('PersonHasNoAccessToAnyIdentitiesException')
tenantAlreadtExistsException = customExceptionClass('Tenant Already Exists','tenantAlreadtExistsException')

jwtHeaderName="jwt-auth-token"
jwtCookieName="jwt-auth-token"

#Also try for the cookie the login page sets this allows swagger to work
##but no renewal here
loginCookieName="usersystemUserCredentials"
