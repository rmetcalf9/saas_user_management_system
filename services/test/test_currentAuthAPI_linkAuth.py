from TestHelperSuperClass import testHelperAPIClient, env, getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse
from constants import masterTenantName, jwtHeaderName, jwtCookieName, DefaultHasAccountRole, masterTenantDefaultSystemAdminRole, objectVersionHeaderName
import json
import copy
from tenants import CreatePerson, GetTenant, _getAuthProvider
from appObj import appObj
from authProviders import authProviderFactory
from authProviders_base import getAuthRecord
import urllib

class currentAuthLinkSetups(testHelperAPIClient):
  pass
  
class test_currentAuthLinkTests(currentAuthLinkSetups):
  def test_deleteNonExistantAuthFails(self):
    pass
    

