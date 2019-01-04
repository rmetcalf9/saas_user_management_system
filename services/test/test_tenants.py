from TestHelperSuperClass import testHelperAPIClient, env
from tenants import GetTenant, CreateTenant, failedToCreateTenantException, Login
from constants import masterTenantName, masterTenantDefaultDescription, masterTenantDefaultAuthProviderMenuText, masterTenantDefaultAuthProviderMenuIconLink, masterTenantDefaultSystemAdminRole, DefaultHasAccountRole
from appObj import appObj

class test_tenants(testHelperAPIClient):
#Actual tests below

  def test_cantCreateTenantWithSameNameAsMaster(self):
    with self.assertRaises(Exception) as context:
      tenant = CreateTenant(appObj, masterTenantName)
    self.checkGotRightException(context,failedToCreateTenantException)


  def test_Master_Tenant_exists(self):
    masterTenant = GetTenant(appObj,masterTenantName)
    self.assertFalse(masterTenant is None, msg="Master Tenant was not created")
    self.assertEquals(masterTenant['Name'], masterTenantName, msg="Master tenant name is wrong")
    self.assertEquals(masterTenant['Description'], masterTenantDefaultDescription, msg="Master tenant default description wrong")
    self.assertFalse(masterTenant['AllowUserCreation'], msg="Master tenant defaults to allowing user creation")

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
    self.assertEqual(len(masterTenant['AuthProviders']),1, msg="No internal Auth Providers found")
    singleAuthProvGUID = ""
    for key in masterTenant['AuthProviders']:
      singleAuthProvGUID = key
      masterTenant['AuthProviders'][singleAuthProvGUID]['guid'] = "ignored"

    self.assertJSONStringsEqual(masterTenant['AuthProviders'][singleAuthProvGUID], expectedAuthProviderJSON, msg="Internal Auth Provider default data incorrect")

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
    