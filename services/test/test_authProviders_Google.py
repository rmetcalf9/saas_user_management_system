from TestHelperSuperClass import testHelperAPIClient
from appObj import appObj
from tenants import GetTenant
import constants
import json
import copy


googleAuthProv001_CREATE = {
  "guid": None,
  "Type": "google",
  "AllowUserCreation": False,
  "MenuText": "Log in with Google",
  "IconLink": "string",
  "ConfigJSON": "{}",
  "saltForPasswordHashing": None
} 

class test_api(testHelperAPIClient):
  def addAuthProvider(self, currentTenantJSON):
    tenantJSON = copy.deepcopy(currentTenantJSON)
    tenantJSON['AuthProviders'].append(copy.deepcopy(googleAuthProv001_CREATE))
    tenantJSON['ObjectVersion'] = currentTenantJSON['ObjectVersion']
    result = self.testClient.put(
      self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants/' + tenantJSON['Name'], 
      headers={ constants.jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantJSON), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))
  
class test_addGoogleAuthProviderToMasterTenant(test_api):    
  def test_createAuth(self):
    result = self.testClient.get(self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants', headers={ constants.jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

    self.addAuthProvider(resultJSON['result'][0])
    
    result = self.testClient.get(self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants', headers={ constants.jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))


