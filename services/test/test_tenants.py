from TestHelperSuperClass import testHelperAPIClient, env
from tenants import GetTenant, CreateTenant, failedToCreateTenantException, Login, UnknownIdentityException
from constants import masterTenantName, masterTenantDefaultDescription, masterTenantDefaultAuthProviderMenuText, masterTenantDefaultAuthProviderMenuIconLink, masterTenantDefaultSystemAdminRole, DefaultHasAccountRole
from appObj import appObj
from constants import authFailedException

class test_tenants(testHelperAPIClient):
#Actual tests below

  def test_cantCreateTenantWithSameNameAsMaster(self):
    with self.assertRaises(Exception) as context:
      tenant = CreateTenant(appObj, masterTenantName)
    self.checkGotRightException(context,failedToCreateTenantException)


  def test_MasterTenantExists(self):
    masterTenant = GetTenant(appObj,masterTenantName)
    self.assertFalse(masterTenant is None, msg="Master Tenant was not created")
    self.assertEquals(masterTenant.getJSONRepresenation()['Name'], masterTenantName, msg="Master tenant name is wrong")
    self.assertEquals(masterTenant.getJSONRepresenation()['Description'], masterTenantDefaultDescription, msg="Master tenant default description wrong")
    self.assertFalse(masterTenant.getJSONRepresenation()['AllowUserCreation'], msg="Master tenant defaults to allowing user creation")

    #Check AuthProvider is correct
    expectedAuthProviderJSON = {
      "guid": "ignored",
      "MenuText": masterTenantDefaultAuthProviderMenuText,
      "IconLink": masterTenantDefaultAuthProviderMenuIconLink,
      "Type":  "internal",
      "AllowUserCreation": False,
      "ConfigJSON": {
        "userSufix": "@internalDataStore"
      }
    }
    self.assertEqual(masterTenant.getNumberOfAuthProviders(),1, msg="No internal Auth Providers found")
    singleAuthProvGUID = ""
    for guid in masterTenant.getAuthProviderGUIDList():
      singleAuthProvGUID=guid

    self.assertJSONStringsEqualWithIgnoredKeys(masterTenant.getAuthProvider(singleAuthProvGUID), expectedAuthProviderJSON, ['guid'], msg="Internal Auth Provider default data incorrect")

    #Check initial user has been created and we could log in
    UserIDandRoles = Login(appObj, masterTenantName, singleAuthProvGUID, {
      'username': env['APIAPP_DEFAULTHOMEADMINUSERNAME'],
      'password': env['APIAPP_DEFAULTHOMEADMINPASSWORD']
    })
    #An exception is raised if the login fails
    expectedRoles = {
      "UserID": env['APIAPP_DEFAULTHOMEADMINUSERNAME'],
      "TenantRoles": {
        "usersystem": [masterTenantDefaultSystemAdminRole, DefaultHasAccountRole]
       }
    }
    self.assertJSONStringsEqual(UserIDandRoles, expectedRoles, msg="Returned roles incorrect")
    
  def test_StandardUserInvalidPassword(self):
    masterTenant = GetTenant(appObj,masterTenantName)
    self.assertEqual(masterTenant.getNumberOfAuthProviders(),1, msg="No internal Auth Providers found")
    singleAuthProvGUID = ""
    for guid in masterTenant.getAuthProviderGUIDList():
      singleAuthProvGUID=guid

    with self.assertRaises(Exception) as context:
      UserIDandRoles = Login(appObj, masterTenantName, singleAuthProvGUID, {
        'username': env['APIAPP_DEFAULTHOMEADMINUSERNAME'],
        'password': env['APIAPP_DEFAULTHOMEADMINPASSWORD'] + 'Extra bit to make password wrong'
      })
    self.checkGotRightException(context,authFailedException)

  def test_StandardUserInvalidUsername(self):
    masterTenant = GetTenant(appObj,masterTenantName)
    self.assertEqual(masterTenant.getNumberOfAuthProviders(),1, msg="No internal Auth Providers found")
    singleAuthProvGUID = ""
    for guid in masterTenant.getAuthProviderGUIDList():
      singleAuthProvGUID=guid

    with self.assertRaises(Exception) as context:
      UserIDandRoles = Login(appObj, masterTenantName, singleAuthProvGUID, {
        'username': env['APIAPP_DEFAULTHOMEADMINUSERNAME'] + 'Extra bit to make username wrong',
        'password': env['APIAPP_DEFAULTHOMEADMINPASSWORD']
      })
    self.checkGotRightException(context,authFailedException)

  def test_StandardUserLoginToInvalidIdentity(self):
    masterTenant = GetTenant(appObj,masterTenantName)
    self.assertEqual(masterTenant.getNumberOfAuthProviders(),1, msg="No internal Auth Providers found")
    singleAuthProvGUID = ""
    for guid in masterTenant.getAuthProviderGUIDList():
      singleAuthProvGUID=guid

    with self.assertRaises(Exception) as context:
      UserIDandRoles = Login(appObj, masterTenantName, singleAuthProvGUID, {
        'username': env['APIAPP_DEFAULTHOMEADMINUSERNAME'],
        'password': env['APIAPP_DEFAULTHOMEADMINPASSWORD']
      }, 'invalid_identity_guid')
    self.checkGotRightException(context,UnknownIdentityException)

