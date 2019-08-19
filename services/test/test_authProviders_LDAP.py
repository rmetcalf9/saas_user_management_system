from TestHelperSuperClass import AddAuth, testHelperAPIClient, wipd, httpOrigin, getTwoWayEncryptedPasswordUsingSameMethodAsJavascriptFrontendShouldUse
from appObj import appObj
import constants
import json
import copy
import os
from tenants import GetTenant, CreateUser
from persons import CreatePerson
from users import associateUserWithPerson

LDAPAuthProv001_CREATE_configJSON = {
  "Timeout": 60,
  "Host": "unixldap.somehost.com",
  "Port": "123",
  "UserBaseDN": "ou=People,ou=everyone,dc=somehost,dc=com",
  "UserAttribute": "uid",
  "GroupBaseDN": "ou=Group,ou=everyone,dc=somehost,dc=com",
  "GroupAttribute": "cn",
  "GroupMemberField": "memberUid",
  "GroupWhiteList": "group1,group2,group3",
  "userSufix": "@TestOrgLDAP"
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

ldapUsername = "ldapuserNameTest001"
ldapPassword = "ldapPASSTest001"

class authProviderHelperFunctions(testHelperAPIClient):
  def addAuthProvider(self, currentTenantJSON, authProviderDICT, expectedResult=200):
    tenantJSON = copy.deepcopy(currentTenantJSON)
    tenantJSON['AuthProviders'].append(copy.deepcopy(authProviderDICT))
    tenantJSON['ObjectVersion'] = currentTenantJSON['ObjectVersion']
    result = self.testClient.put(
      self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants/' + tenantJSON['Name'],
      headers={ constants.jwtHeaderName: self.getNormalJWTToken()},
      data=json.dumps(tenantJSON),
      content_type='application/json'
    )
    if expectedResult==200:
      self.assertEqual(result.status_code, 200, msg="Failed to add auth - " + result.get_data(as_text=True))
      return json.loads(result.get_data(as_text=True))
    return result

  def setupLDAPAuthOnMainTenantForTests(self, override_JSON = LDAPAuthProv001_CREATE, tenantName = constants.masterTenantName, expectedAddAuthResultStatusCode = 200):
    result = self.testClient.get(self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants', headers={ constants.jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    AddAuthRes = None
    resultJSON = json.loads(result.get_data(as_text=True))
    for x in resultJSON['result']:
      if x['Name'] == tenantName:
        AddAuthRes = self.addAuthProvider(x, override_JSON, expectedResult=expectedAddAuthResultStatusCode)

    result2 = self.testClient.get(self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants', headers={ constants.jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result2.status_code, 200)
    resultJSON2 = json.loads(result2.get_data(as_text=True))
    for x in resultJSON2['result']:
      if x['Name'] == tenantName:
        return {
          "Tenant": x,
          "AddAuthRes": AddAuthRes
        }
    return {
      "Tenant": None,
      "AddAuthRes": AddAuthRes
    }

  def loginAsUserUsingLDAP(self, tenant, authProviderDICT, username, password, expectedResults = [200]):
    hashedPassword = getTwoWayEncryptedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(
      username,
      password,
      authProviderDICT['saltForPasswordHashing']
    )

    loginJSON = {
      "authProviderGUID": authProviderDICT['guid'],
      "credentialJSON": {
        "username": username,
        "password": hashedPassword
       }
    }
    result2 = self.testClient.post(
      self.loginAPIPrefix + '/' + tenant + '/authproviders',
      data=json.dumps(loginJSON),
      content_type='application/json',
      headers={"Origin": httpOrigin}
    )
    for x in expectedResults:
      if result2.status_code == x:
        return json.loads(result2.get_data(as_text=True))
    print(result2.get_data(as_text=True))
    self.assertFalse(True, msg="Login status_code was " + str(result2.status_code) + " expected one of " + str(expectedResults))
    return None

  def createLDAPUser(self, username, storeConnection, authProvGUID, appObj=appObj):
    masterTenant = GetTenant(constants.masterTenantName, storeConnection, appObj=appObj)
    CreateUser(appObj, {"user_unique_identifier": username, "known_as": username}, constants.masterTenantName, "test/createLDAPUser", storeConnection)
    person = CreatePerson(appObj, storeConnection, None, 'a','b','c')
    authData = AddAuth(
      appObj, constants.masterTenantName, authProvGUID, {
        "username": username
      },
      person['guid'],
      storeConnection
    )
    associateUserWithPerson(appObj, username, person['guid'], storeConnection)
    return {
      'authProvGUID': authProvGUID,
      'person': person
    }


@wipd
class test_addGoogleAuthProviderToMasterTenant(authProviderHelperFunctions):
  def test_createAuth(self):
    resultJSON2 = self.setupLDAPAuthOnMainTenantForTests()
    self.assertEqual(resultJSON2["Tenant"]["AuthProviders"][0]["Type"],"internal", msg="First auth prov type wrong")
    self.assertEqual(resultJSON2["Tenant"]["AuthProviders"][1]["Type"],"LDAP", msg="First auth prov type wrong")

  def test_turnOnUserCreationFails(self):
    resultJSON2 = self.setupLDAPAuthOnMainTenantForTests()

    #Turn on user creation on auth prov
    toLoad = copy.deepcopy(resultJSON2["Tenant"])
    self.assertEqual(toLoad["AuthProviders"][1]["Type"],"LDAP", msg="First auth prov type wrong")
    toLoad["AuthProviders"][1]["AllowUserCreation"] = True
    tenantDict3 = self.updateTenant(toLoad, [200])

  def test_loginUserWithSingleGroupMatchingSingleGroupInWhitelist_NOUSERCREATIONEXISTINGUSER(self):
    resultJSON2 = self.setupLDAPAuthOnMainTenantForTests()
    self.assertEqual(resultJSON2["Tenant"]["AuthProviders"][1]["Type"],"LDAP", msg="First auth prov type wrong")
    ldapAuthProv = copy.deepcopy(resultJSON2["Tenant"]["AuthProviders"][1])

    #Create user
    def dbfn(storeConnection):
      return self.createLDAPUser(
        username=ldapUsername,
        storeConnection=storeConnection,
        authProvGUID=ldapAuthProv["guid"]
      )
    createdUserData = appObj.objectStore.executeInsideTransaction(dbfn)

    self.loginAsUserUsingLDAP(
      tenant=constants.masterTenantName,
      authProviderDICT=ldapAuthProv,
      username=ldapUsername,
      password=ldapPassword,
      expectedResults = [200]
    )


  '''
  def test_loginUserWithSingleGroupMatchingSingleGroupInWhitelist_USERCREATIONREQUIREDANDALLOWED(self):
    resultJSON2 = self.setupLDAPAuthOnMainTenantForTests(override_JSON=LDAPAuthProv001_CREATE_withAllowCreate)
    self.assertEqual(resultJSON2["Tenant"]["AuthProviders"][1]["Type"],"LDAP", msg="First auth prov type wrong")
    ldapAuthProv = copy.deepcopy(resultJSON2["Tenant"]["AuthProviders"][1])

    self.loginAsUserUsingLDAP(
      tenant=constants.masterTenantName,
      authProviderDICT=ldapAuthProv,
      username=ldapUsername,
      password=ldapPassword,
      expectedResults = [200]
    )
  '''
  def test_loginUserWithSingleGroupMatchingSingleGroupInWhitelist_USERCREATIONREQUIREDBUTNOTALLOWED(self):
    resultJSON2 = self.setupLDAPAuthOnMainTenantForTests()
    self.assertEqual(resultJSON2["Tenant"]["AuthProviders"][1]["Type"],"LDAP", msg="First auth prov type wrong")
    ldapAuthProv = copy.deepcopy(resultJSON2["Tenant"]["AuthProviders"][1])

    resp = self.loginAsUserUsingLDAP(
      tenant=constants.masterTenantName,
      authProviderDICT=ldapAuthProv,
      username=ldapUsername,
      password=ldapPassword,
      expectedResults = [401]
    )

    self.assertEqual(resp["message"],"authFailedException",msg="Wrong error message")

#bad password fails

#test_loginUserWithTwoGroupsONEMatching

#test_loginUserFAILWithSingleGroupMatchingSingleGroupInWhitelist

#test_loginUserFAILWithTwoGroupsONEMatching
