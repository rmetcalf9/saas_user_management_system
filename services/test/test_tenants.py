from TestHelperSuperClass import testHelperAPIClient
from tenants import GetTenant, CreateTenant, failedToCreateTenantException
from constants import masterTenantName, masterTenantDefaultDescription
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

    #TODO Check AuthProvider is correct
