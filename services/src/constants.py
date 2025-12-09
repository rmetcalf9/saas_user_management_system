# File to hold constants

masterTenantName="usersystem"
masterTenantDefaultDescription="Master Tenant for User Management System"
masterTenantDefaultAuthProviderMenuText="Website account login"
masterTenantDefaultAuthProviderMenuTextInternalAuthLinkText="Link Website Account"
masterTenantDefaultAuthProviderMenuIconLink=None
masterTenantDefaultSystemAdminRole="systemadmin"
masterTenantDefaultTenantBannerHTML=""
masterTenantDefaultSelectAuthMessage="How do you want to verify who you are?"
DefaultHasAccountRole="hasaccount"
SecurityEndpointAccessRole="securityTest"


conDefaultUserGUID = "FORCED-CONSTANT-TESTING-GUID"
conTestingDefaultPersonGUID = "FORCED-CONSTANT-TESTING-PERSON-GUID"

#This is also used in frontend quasar app
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

class customUnauthorizedExceptionClass(Exception):
  id = None
  text = None
  def __init__(self, text, iid=None):
    if iid is None:
      self.id = text
    else:
      self.id = iid
    self.text = text

#PersonHasNoAccessToAnyIdentitiesException = customUnauthorizedExceptionClass('PersonHasNoAccessToAnyIdentitiesException')

authProviderNotFoundException = customExceptionClass('authProviderNotFoundException','authProviderNotFoundException')
authFailedException = customExceptionClass('authFailedException')
authNotFoundException = customExceptionClass('authNotFoundException','authNotFoundException')
tenantAlreadtExistsException = customExceptionClass('Tenant Already Exists','tenantAlreadtExistsException')
tenantDosentExistException = customExceptionClass('Tenant Dosen\'t Exist','tenantDosentExistException')
ShouldNotSupplySaltWhenCreatingAuthProvException = customExceptionClass('Should not supply salt when creating new auth prov', 'ShouldNotSupplySaltWhenCreatingAuthProvException')
cantUpdateExistingAuthProvException = customExceptionClass('can\'t Update Existing Auth Prov', 'cantUpdateExistingAuthProvException')
cantDeleteMasterTenantException = customExceptionClass('can\'t delete master tenant', 'cantDeleteMasterTenantException')
personDosentExistException = customExceptionClass('Person Dosen\'t Exist','personDosentExistException')
userCreationNotAllowedException = customExceptionClass('User Creation Not Allowed', 'userCreationNotAllowedException')


class invalidPersonInToken(Exception):
  text = "invalidPersonInToken"
class invalidUserInToken(Exception):
  text = "invalidUserInToken"


class notImplemented(customExceptionClass):
  def __init__(self, text):
    self.text = text + ' Not Implemented'

jwtHeaderName="jwt-auth-token"
jwtCookieName="jwt-auth-token"
objectVersionHeaderName="object-version-id"

#Also try for the cookie the login page sets this allows swagger to work
##but no renewal here
loginCookieName="usersystemUserCredentials"


#Object Type NAmes
objectType_users_associatedPersons = "usersAssociatedPersons"  #was users_associatedPersons but I had to change due to dynamoDB