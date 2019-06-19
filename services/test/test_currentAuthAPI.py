from TestHelperSuperClass import httpOrigin, testHelperAPIClient, env, getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse
from constants import masterTenantName, jwtHeaderName, jwtCookieName, DefaultHasAccountRole, masterTenantDefaultSystemAdminRole, objectVersionHeaderName
import json
import copy
from tenants import CreatePerson, GetTenant, _getAuthProvider
from appObj import appObj
from authProviders import authProviderFactory
from authProviders_base import getAuthRecord



class test_securityTests(testHelperAPIClient):
  def test_get_currentAuthInfo_noAccessWithoutHeader(self):
    result = self.testClient.get(self.currentAuthAPIPrefix + '/' + masterTenantName + '/currentAuthInfo', headers={})
    self.assertEqual(result.status_code, 401, msg='noAccess Test failed - ' + result.get_data(as_text=True))


  def test_get_currentAuthInfo_forDefaultUser(self):
    result = self.testClient.get(self.currentAuthAPIPrefix + '/' + masterTenantName + '/currentAuthInfo', headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

    expectedAll = {
      'currentlyUsedAuthProviderGuid': 'DummyCurrentlyAuthedGUID',
      'currentlyUsedAuthKey': 'DummyAuthKey'
    }
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON, expectedAll, ["loggedInPerson", "loggedInUser"], msg='Did not get expected Person result')

    expectedPersonResult = {
      "ObjectVersion": "1",
      "associatedUsers": [{
        "ObjectVersion": "4",
        "TenantRoles": [{"TenantName": "usersystem", "ThisTenantRoles": ["hasaccount", "securityTest", "systemadmin"]}],
        "UserID": "FORCED-CONSTANT-TESTING-GUID",
        "associatedPersonGUIDs": ["FORCED-CONSTANT-TESTING-PERSON-GUID"],
        "creationDateTime": "2019-04-30T09:03:35.241658+00:00",
        "known_as": "AdminTestSet",
        "lastUpdateDateTime": "2019-04-30T09:03:35.241718+00:00",
        "other_data": {"createdBy": "init/CreateMasterTenant"}
      }],
      "creationDateTime": "2019-04-30T09:03:35.241723+00:00",
      "guid": "FORCED-CONSTANT-TESTING-PERSON-GUID",
      "lastUpdateDateTime": "2019-04-30T09:03:35.241723+00:00",
      "personAuths": [{
        "AuthProviderGUID": "9a649f23-e8b4-42ba-b613-9bac7911980b",
        "AuthProviderType": "internal",
        "AuthUserKey": "AdminTestSet@internalDataStore_`@\\/'internal",
        "known_as": "AdminTestSet",
        "tenantName": "usersystem"
       }]
    }
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON["loggedInPerson"], expectedPersonResult, ["associatedUsers", "personAuths", "creationDateTime", "lastUpdateDateTime"], msg='Did not get expected Person result')
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON["loggedInPerson"]["associatedUsers"][0], expectedPersonResult["associatedUsers"][0], ["creationDateTime", "lastUpdateDateTime"], msg='Did not get expected Person->associatedUsers result')
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON["loggedInPerson"]["personAuths"][0], expectedPersonResult["personAuths"][0], ["AuthProviderGUID"], msg='Did not get expected Person->personAuths result')


    expectedUserResult = {
      "ObjectVersion": "4",
      "TenantRoles": [{"TenantName": "usersystem", "ThisTenantRoles": ["hasaccount", "securityTest", "systemadmin"]}],
      "UserID": "FORCED-CONSTANT-TESTING-GUID",
      "associatedPersonGUIDs": ["FORCED-CONSTANT-TESTING-PERSON-GUID"],
      "creationDateTime": "2019-04-30T09:09:37.156689+00:00",
      "known_as": "AdminTestSet",
      "lastUpdateDateTime": "2019-04-30T09:09:37.156709+00:00",
      "other_data": {"createdBy": "init/CreateMasterTenant"}
    }

    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON["loggedInUser"], expectedUserResult, ["creationDateTime", "lastUpdateDateTime"], msg='Did not get expected User result')

  def test_authOperaiton_internal_resetPassword_to_same_errors(self):
    result = self.testClient.get(
      self.loginAPIPrefix + '/' + masterTenantName + '/authproviders',
      headers={"Origin": httpOrigin}
    )
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))
    masterAuthProviderGUID = resultJSON[ 'AuthProviders' ][0]['guid']

    newHashedPassword = self.getDefaultHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(resultJSON[ 'AuthProviders' ][0]['saltForPasswordHashing'])

    resetPasswordCmd = {
      "authProviderGUID": masterAuthProviderGUID,
      "credentialJSON": {
        "username": env['APIAPP_DEFAULTHOMEADMINUSERNAME'],
        "password": self.getDefaultHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(resultJSON[ 'AuthProviders' ][0]['saltForPasswordHashing'])
      },
      "operationData": {"newPassword": newHashedPassword },
      "operationName": "ResetPassword"
    }
    result = self.testClient.post(
      self.currentAuthAPIPrefix + '/' + masterTenantName + '/currentAuthInfo',
      headers={ jwtHeaderName: self.getNormalJWTToken()},
      data=json.dumps(resetPasswordCmd),
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg="Reset password failed - " + result.get_data(as_text=True))

  def test_authOperaiton_internal_resetPassword(self):
    newPassword = 'ABC123dfsfdfd'

    result = self.testClient.get(
      self.loginAPIPrefix + '/' + masterTenantName + '/authproviders',
      headers={"Origin": httpOrigin}
    )
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))
    masterAuthProviderGUID = resultJSON[ 'AuthProviders' ][0]['guid']

    #Log in with orig password
    self.loginAsUser(masterTenantName, resultJSON[ 'AuthProviders' ][0], env['APIAPP_DEFAULTHOMEADMINUSERNAME'], env['APIAPP_DEFAULTHOMEADMINPASSWORD'])

    newHashedPassword = getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(env['APIAPP_DEFAULTHOMEADMINUSERNAME'], newPassword, resultJSON[ 'AuthProviders' ][0]['saltForPasswordHashing'])
    resetPasswordCmd = {
      "authProviderGUID": masterAuthProviderGUID,
      "credentialJSON": {
        "username": env['APIAPP_DEFAULTHOMEADMINUSERNAME'],
        "password": self.getDefaultHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(resultJSON[ 'AuthProviders' ][0]['saltForPasswordHashing'])
      },
      "operationData": {"newPassword": newHashedPassword },
      "operationName": "ResetPassword"
    }
    result = self.testClient.post(
      self.currentAuthAPIPrefix + '/' + masterTenantName + '/currentAuthInfo',
      headers={ jwtHeaderName: self.getNormalJWTToken()},
      data=json.dumps(resetPasswordCmd),
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 200, msg="Reset password failed - " + result.get_data(as_text=True))

    #Log in with new password
    self.loginAsUser(masterTenantName, resultJSON[ 'AuthProviders' ][0], env['APIAPP_DEFAULTHOMEADMINUSERNAME'], newPassword)
