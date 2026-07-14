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
authFailedException = customExceptionClass('authFailedException', 'authFailedException')
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

#Apple sign in constants
apple_signon_public_key_url = "https://appleid.apple.com/auth/keys"
apple_iss = "https://appleid.apple.com"

#This key is ONLY used when the app is in testing mode
testmodersakeyforjwtsigning = {
    "alg": "RS256",
    "e": "AQAB",
    "kid": "TESTINGKID",
    "kty": "RSA",
    "n": "lSJXgvDhHLXlMPqFiOnU6umReqefLHKLFh4kgdhP71BlDxEa_yNtYbrszflO1Od-VkGkV615LxQGuOT6Un9S58xuPmrIuHF48AIUCh4FBsrI-GBFML_6pi1tGLGZq7q59k5N2QWVRx7M-d714Uu0wO2O1JjdcvE6-s2myRlFLYK0Z4635AU6lgCWHNJzJlYp7xyISbOkY10ayJ9C8LIU0tCgXsREEE-aNIP_Vo0o7GS-kqqb4s6mwf9SEFSFqqK5GN0cJVXjUl3VLUDzJp3WXvkSWKu5eK1eraeIwWA9jTjcsUGO0XnqQvlN8AkQbaXoCz8dK8VKsPqiovIpruE7TQ",
    "use": "sig"
}
#note: for a valid token aud = service id. (app.socialclubhub.login)
