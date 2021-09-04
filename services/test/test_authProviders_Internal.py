import TestHelperSuperClass
import constants
import json
import copy
from authProviders_Internal import getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse
from appObj import appObj

InternalAuthProv001_CREATE_configJSON = {
  "userSufix": "@internalDataStore"
}


InternalAuthProv001_CREATE = {
  "guid": None,
  "Type": "internal",
  "AllowUserCreation": True,
  "AllowLink": False,
  "AllowUnlink": False,
  "LinkText": 'Link',
  "MenuText": "Log in site password",
  "IconLink": "string",
  "ConfigJSON": json.dumps(InternalAuthProv001_CREATE_configJSON),
  "saltForPasswordHashing": None
}

class helpers(TestHelperSuperClass.testHelperAPIClient):
  def getTenantList(self):
    result = self.testClient.get(self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants', headers={ constants.jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    return json.loads(result.get_data(as_text=True))

  def setupInternalAuthOnMainTenantForTests(self, tenantName = constants.masterTenantName):
    authProvDict = copy.deepcopy(InternalAuthProv001_CREATE)
    tenantList = self.getTenantList()["result"]
    addAuthRes = None
    for x in tenantList:
      if x['Name'] == tenantName:
        for curAuth in x["AuthProviders"]:
          if curAuth["Type"] == "internal":
            raise Exception("Test will not work with mutiple auths of same type")
        addAuthRes = self.addAuthProvider2(x, authProvDict)

    if addAuthRes is None:
      raise Exception("Invalid tenant name")

    #return the auth provider we just created
    for x in addAuthRes["AuthProviders"]:
      if x["Type"] == authProvDict["Type"]:
        return x

    raise Exception("could not find created auth with guid")

  def setAllowUserCreationOnTenant(self, tenantName):
    tenantList = self.getTenantList()["result"]
    for x in tenantList:
      if x['Name'] == tenantName:
        newTenantDict = copy.deepcopy(x)
        newTenantDict["AllowUserCreation"] = True

        result = self.testClient.put(
          self.adminAPIPrefix + '/' + TestHelperSuperClass.masterTenantName + '/tenants/' + newTenantDict['Name'],
          headers={ constants.jwtHeaderName: self.getNormalJWTToken()},
          data=json.dumps(newTenantDict),
          content_type='application/json'
        )
        self.assertEqual(result.status_code, 200)
        return

    raise Exception("Could not find tenant ", tenantName)

  def loginUser(self, tenantName, username, password, authProvider):
    hashedpassword = getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(
      appObj=appObj,
      username=username,
      password=password,
      tenantAuthProvSalt=authProvider["saltForPasswordHashing"]
    )

    loginJSON = {
      "authProviderGUID": authProvider["guid"],
      "credentialJSON": {
        "username": username,
        "password": hashedpassword.decode()
       }
    }
    result2 = self.testClient.post(
      self.loginAPIPrefix + '/' + tenantName + '/authproviders',
      data=json.dumps(loginJSON),
      content_type='application/json',
      headers={"Origin": TestHelperSuperClass.httpOrigin}
    )
    self.assertEqual(result2.status_code, 200, msg="Failed login " + result2.get_data(as_text=True))

    return json.loads(result2.get_data(as_text=True))


@TestHelperSuperClass.wipd
class test_authProviders_Internal(helpers):

  def test_createAndLoginAsUser(self):
    tenantDICT = self.createTenantForTesting(TestHelperSuperClass.tenantWithNoAuthProviders)
    tenantName = tenantDICT["Name"]

    print("Test using tenant name", tenantName)

    newAuth = self.setupInternalAuthOnMainTenantForTests(tenantName=tenantName)
    self.setAllowUserCreationOnTenant(tenantName=tenantName)

    username = "testuser"
    password = "testpassword"

    regResult = self.registerInternalUser(
      tenantName=tenantName,
      username=username,
      password=password,
      authProvider=newAuth
    )

    loginRes = self.loginUser(
      tenantName=tenantName,
      username=username,
      password=password,
      authProvider=newAuth
    )
    #if we get here login is sucessful
