from TestHelperSuperClass import testHelperAPIClient, wipd
import constants
import json
import copy
import os

LDAPAuthProv001_CREATE_configJSON = {
  "Timeout": 60,
  "Host": "unixldap.somehost.com",
  "Port": "123",
  "UserBaseDN": "ou=People,ou=everyone,dc=somehost,dc=com",
  "UserAttribute": "uid",
  "GroupBaseDN": "ou=Group,ou=everyone,dc=somehost,dc=com",
  "GroupAttribute": "cn",
  "GroupMemberField": "memberUid",
  "GroupWhiteList": "group1,group2,group3"
}

LDAPAuthProv001_CREATE = {
  "guid": None,
  "Type": "LDAP",
  "AllowUserCreation": False,
  "AllowLink": False,
  "AllowUnlink": False,
  "LinkText": 'Link',
  "MenuText": "Log in using LDAP",
  "IconLink": "string",
  "ConfigJSON": json.dumps(LDAPAuthProv001_CREATE_configJSON),
  "saltForPasswordHashing": None
}
LDAPAuthProv001_CREATE_withAllowCreate = copy.deepcopy(LDAPAuthProv001_CREATE)
LDAPAuthProv001_CREATE_withAllowCreate['AllowUserCreation'] = True


class authProviderHelperFunctions(testHelperAPIClient):
  def addAuthProvider(self, currentTenantJSON, authProviderDICT):
    tenantJSON = copy.deepcopy(currentTenantJSON)
    tenantJSON['AuthProviders'].append(copy.deepcopy(authProviderDICT))
    tenantJSON['ObjectVersion'] = currentTenantJSON['ObjectVersion']
    result = self.testClient.put(
      self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants/' + tenantJSON['Name'],
      headers={ constants.jwtHeaderName: self.getNormalJWTToken()},
      data=json.dumps(tenantJSON),
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 200, msg="Failed to add auth - " + result.get_data(as_text=True))
    return json.loads(result.get_data(as_text=True))

  def setupLDAPAuthOnMainTenantForTests(self, override_JSON = LDAPAuthProv001_CREATE, tenantName = constants.masterTenantName):
    result = self.testClient.get(self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants', headers={ constants.jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))
    for x in resultJSON['result']:
      if x['Name'] == tenantName:
        self.addAuthProvider(x, override_JSON)

    result2 = self.testClient.get(self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants', headers={ constants.jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result2.status_code, 200)
    resultJSON2 = json.loads(result2.get_data(as_text=True))
    for x in resultJSON2['result']:
      if x['Name'] == tenantName:
        return x
    return None


@wipd
class test_addGoogleAuthProviderToMasterTenant(authProviderHelperFunctions):
  def test_createAuth(self):
    resultJSON2 = self.setupLDAPAuthOnMainTenantForTests()

    #expectedResult = copy.deepcopy(googleAuthProv001_CREATE)
    #expectedResult["StaticlyLoadedData"] = {"client_id": "someGoogleID.apps.googleusercontent.com"}

    #self.assertJSONStringsEqualWithIgnoredKeys(resultJSON2["AuthProviders"][1], expectedResult, ["guid","saltForPasswordHashing","StaticlyLoadedData"], msg='JSON of google Auth provider not right')
    #self.assertJSONStringsEqualWithIgnoredKeys(resultJSON2["AuthProviders"][1]["StaticlyLoadedData"], expectedResult["StaticlyLoadedData"], ["client_id"], msg='StaticallyLoadedData Mismatch')
    #if not resultJSON2["AuthProviders"][1]["StaticlyLoadedData"]["client_id"].endswith(".apps.googleusercontent.com"):
    #  self.assertFalse(True,msg="Invalid Client ID")

    self.assertTrue(False, msg="TO COMPLETE")
