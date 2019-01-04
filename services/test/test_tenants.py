from TestHelperSuperClass import testHelperAPIClient
from tenants import GetTenant, CreateTenant, failedToCreateTenantException
from constants import masterTenantName, masterTenantDefaultDescription, masterTenantDefaultAuthProviderMenuText, masterTenantDefaultAuthProviderMenuIconLink
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
      "Type":  "Internal",
      "AllowUserCreation": False,
      "ConfigJSON": {
        "PasswordStoreObjectType": "internalDataStore"
      }
    }
    self.assertEqual(len(masterTenant['AuthProviders']),1, msg="No internal Auth Providers found")
    masterTenant['AuthProviders'][0]['guid'] = "ignored"
    self.assertJSONStringsEqual(masterTenant['AuthProviders'][0], expectedAuthProviderJSON, msg="Internal Auth Provider default data incorrect")

    #TODO Check initial user has been created