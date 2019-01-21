from TestHelperSuperClass import testHelperAPIClient, env
from apiSecurity import verifyAPIAccessUserLoginRequired

from constants import masterTenantName

class test_apiSecurity(testHelperAPIClient):

  def test_returnsSuccessWithNoCookieFails(self):
    self.assertFalse(verifyAPIAccessUserLoginRequired(masterTenantName, None))
