from ticketManager__Common_API import ticketManagerAPICommonUtilsClass
import copy
import json
import constants
import TestHelperSuperClass
from unittest.mock import patch
import jwt
from base64 import b64decode

apple_test_service_id = "TEST_SERVICE_ID"

appleAuthProv001_CREATE = {
  "guid": None,
  "Type": "apple",
  "AllowUserCreation": False,
  "AllowLink": False,
  "AllowUnlink": False,
  "LinkText": 'Link',
  "MenuText": "Log in with Apple",
  "IconLink": "string",
  "ConfigJSON": "{\"service_id\": \"" + apple_test_service_id + "\"}",
  "saltForPasswordHashing": None
}
appleAuthProv001_CREATE_missing_service_id = {
  "guid": None,
  "Type": "apple",
  "AllowUserCreation": False,
  "AllowLink": False,
  "AllowUnlink": False,
  "LinkText": 'Link',
  "MenuText": "Log in with Apple",
  "IconLink": "string",
  "ConfigJSON": "{}",
  "saltForPasswordHashing": None
}
appleAuthProv001_CREATE_withAllowCreate = copy.deepcopy(appleAuthProv001_CREATE)
appleAuthProv001_CREATE_withAllowCreate['AllowUserCreation'] = True


appleLoginAccounts = []
appleLoginAccounts.append({
  "identityToken": "AAA"
})
appleLoginAccounts.append({
  "identityToken": "FirstTime",
  "user": {
    "email": "bob@example.com",
    "name": {
        "firstName": "Robert",
        "lastName": "Metcalf"
    }
  }
})

def generateIdentityToken(apple_subject="Default_apple_subject"):
    headers = {
        "alg": "RS256",
        "kid": constants.testmodersakeyforjwtsigning["kid"]
    }
    JWTDict = {
        "iss": constants.apple_iss,
        "aud": apple_test_service_id,
        "sub": apple_subject,
        "email": "user@example.com",
        "email_verified": "true",
        "is_private_email": "false",
    }
    privateKey = {
        "alg": "RS256",
        "d": "F_-IuYdtkiMrGHCX4GpQWuTvBh_HG23rN8nt8f8PDeGQAZatE3Vt-pYL2TFPIC-IQvUZLwq5P3wngMVICtJ2UtqwutaQKi4IWgbblq0x_d_P6zgCqk-aU_dnYNvjcKEBn8MF__BID0PDlEnuoyx9j7Yqj8dxizeKWCWTuzSXzzTEUAd85DHBetYzIpN19ncMhqny4R5v-nJho3lCEnMdE-FuWVr5795DOjfrHBhXmCyUaP_28W4hElTCtFI92Nbqo2F6j8Mgw1ajKlgcW4iTGLF5jPlQiC_eDgZjVyUGCFLTPAf2UVZugFMJqjP-ajTay6-9Jgb_y7wicopDIeEXwQ",
        "dp": "fAbf7O1VLYsDw1kF75tAHFY0HDX0JTwS1uinriVQFz0olt4EWU5bl1rcH2onY-45Z1lzhg5ESgXuEq5V3v0OInsBeLPG3ld9Qv2-TpPJ3-sLG30CxfqTydaLBGBeBpy6GaMHPqj_oE2jtmY5xeW0NDC4mnIyAjoPcidAzAb7Gjk",
        "dq": "Cbs2Yfr2ZLg3lGfJUm6ryQobVo_T4fjAwhQFoo5jPqWaueXA3atv0JLsz3bBDukaiJBBZ-SQ6Ag1Q5Bbqd4YZc1lSRkKDPexK8zfzGzfceF9oGJemUaBeaUc3v-hu9HbyJKM7bLHiS31G_aAemEzDy8SyIBb-Yc7q9jgy7ATtRk",
        "e": "AQAB",
        "kid": "TESTINGKID",
        "kty": "RSA",
        "n": "lSJXgvDhHLXlMPqFiOnU6umReqefLHKLFh4kgdhP71BlDxEa_yNtYbrszflO1Od-VkGkV615LxQGuOT6Un9S58xuPmrIuHF48AIUCh4FBsrI-GBFML_6pi1tGLGZq7q59k5N2QWVRx7M-d714Uu0wO2O1JjdcvE6-s2myRlFLYK0Z4635AU6lgCWHNJzJlYp7xyISbOkY10ayJ9C8LIU0tCgXsREEE-aNIP_Vo0o7GS-kqqb4s6mwf9SEFSFqqK5GN0cJVXjUl3VLUDzJp3WXvkSWKu5eK1eraeIwWA9jTjcsUGO0XnqQvlN8AkQbaXoCz8dK8VKsPqiovIpruE7TQ",
        "p": "yBAN77a4km8-oIoss-LWaup8NNCQCKvjtw6w71CsEaaDZkYmRHuavhBQ6wng7KW_bO3qYn6gG7AHg7kn7LZhf1rj8-j8gPTztb5j8nqUtmEqp33jP7RZhqvupy9HQCq_-om0sIC6xHU_YZT5Q90oFFhee7rYD6bj7kYMB7xy3Fk",
        "q": "vtT1hTw8pL0S5DjRIxUok4ZjBP3jpG8gitxIM8itz1jPFyuRWB041rE1CZ5MHZSQIyTEHAij-LtPzPRzYM4TmhrkxJUnOFvHRshbaGG7k5rZYjO0SopmCzqQBKJzKmfXIM-Mz7gW-iO31f4yAuLZRPNvWFTpAtmjZU7ytv1ZaBU",
        "qi": "X8BtNLIbJGaOWjhadYHSu_7VwYGOFZvtzc1d7oNMKWBmAxQo-mzUR-Ausyz4QiNAXAV8ovt5YzLjcholq_v4K9pqONNCld7THMPh58O_qBjlUvmBAVZkdbf9NBEye7VTDHdveyVGeZLo7Gn9vOW3wHCm9lbfeJuMAlJ7jFo8IhM",
        "use": "sig"
    }
    encodedJWT = jwt.encode(
        JWTDict,
        jwt.PyJWK.from_dict(privateKey).key,
        algorithm="RS256",
        headers={
            "kid": privateKey["kid"]
        },
    )
    return encodedJWT

class helpers(ticketManagerAPICommonUtilsClass):
    def addAuthProvider(self, currentTenantJSON, authProviderDICT):
        tenantJSON = copy.deepcopy(currentTenantJSON)
        tenantJSON['AuthProviders'].append(copy.deepcopy(authProviderDICT))
        tenantJSON['ObjectVersion'] = currentTenantJSON['ObjectVersion']
        result = self.testClient.put(
            self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants/' + tenantJSON['Name'],
            headers={constants.jwtHeaderName: self.getNormalJWTToken()},
            data=json.dumps(tenantJSON),
            content_type='application/json'
        )
        self.assertEqual(result.status_code, 200, msg="Failed to add auth - " + result.get_data(as_text=True))
        return json.loads(result.get_data(as_text=True))

    def setupAppleAuthOnMainTenantForTests(self, override_JSON = appleAuthProv001_CREATE, tenantName = constants.masterTenantName):
        result = self.testClient.get(self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants', headers={ constants.jwtHeaderName: self.getNormalJWTToken()})
        self.assertEqual(result.status_code, 200)
        resultJSON = json.loads(result.get_data(as_text=True))
        for x in resultJSON['result']:
          if x['Name'] == tenantName:
            self.addAuthProvider(x, override_JSON)

        result2 = self.testClient.get(self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants',
                                      headers={constants.jwtHeaderName: self.getNormalJWTToken()})
        self.assertEqual(result2.status_code, 200)
        resultJSON2 = json.loads(result2.get_data(as_text=True))
        for x in resultJSON2['result']:
            if x['Name'] == tenantName:
                return x
        return None

    def loginWithApple(self, appleLoginAccountNum, tenantName, authProviderDICT, expectedResults, ticketToPass=None):
        creds = copy.deepcopy(appleLoginAccounts[appleLoginAccountNum])
        creds["identityToken"] = generateIdentityToken()
        loginJSON = {
          "credentialJSON": creds,
          "authProviderGUID": authProviderDICT['guid']
        }
        if ticketToPass is not None:
          loginJSON["ticket"] = ticketToPass
        result2 = None
        with patch("AuthProviders.authProviders_Google.authProviderGoogle._enrichCredentialDictForAuth", return_value=appleLoginAccounts[appleLoginAccountNum]) as mock_loadStaticData:
          result2 = self.testClient.post(
            self.loginAPIPrefix + '/' + tenantName + '/authproviders',
            data=json.dumps(loginJSON),
            content_type='application/json',
            headers={"Origin": TestHelperSuperClass.httpOrigin}
          )

        for x in expectedResults:
          if x == result2.status_code:
            return json.loads(result2.get_data(as_text=True))
        self.assertFalse(True, msg="Login status_code was " + str(result2.status_code) + " expected one of " + str(expectedResults) + " " + result2.get_data(as_text=True))
        return None


class test_authproviders_apple(helpers):
  def test_createAuth(self):
    resultJSON2 = self.setupAppleAuthOnMainTenantForTests()

    expectedResult = copy.deepcopy(appleAuthProv001_CREATE)
    expectedResult["StaticlyLoadedData"] = {"client_id": "XX"}

    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON2["AuthProviders"][1], expectedResult, ["guid","saltForPasswordHashing","StaticlyLoadedData"], msg='JSON of apple Auth provider not right')
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON2["AuthProviders"][1]["StaticlyLoadedData"], expectedResult["StaticlyLoadedData"], ["client_id"], msg='StaticallyLoadedData Mismatch')
    self.assertEqual(resultJSON2["AuthProviders"][1]["StaticlyLoadedData"]["client_id"], json.loads(appleAuthProv001_CREATE["ConfigJSON"])["service_id"])

  def test_createAuthMissingServiceId(self):
    result = self.testClient.get(self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants', headers={ constants.jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

    tenantJSON = copy.deepcopy(resultJSON['result'][0])
    tenantJSON['AuthProviders'].append(copy.deepcopy(appleAuthProv001_CREATE_missing_service_id))
    tenantJSON['ObjectVersion'] = resultJSON['result'][0]['ObjectVersion']
    result = self.testClient.put(
      self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants/' + tenantJSON['Name'],
      headers={ constants.jwtHeaderName: self.getNormalJWTToken()},
      data=json.dumps(tenantJSON),
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg='Create should have failed')

  def test_authFailsWithNoAppleAuthsAccepted(self):
    #Test authentication via apple.
    ## Must use mocks

    resultJSON2 = self.setupAppleAuthOnMainTenantForTests()
    appleAuthProvider = resultJSON2["AuthProviders"][1]

    result2JSON = self.loginWithApple(
        0,
        constants.masterTenantName,
        appleAuthProvider,
        [401]
    )

  def test_authWithUserCreation(self):
    #Test authentication via apple.
    ## Must use mocks
    tenantDict = self.createTenantWithAuthProvider(
        TestHelperSuperClass.tenantWithNoAuthProviders,
        True,
        TestHelperSuperClass.sampleInternalAuthProv001_CREATE_WithAllowUserCreation
    )

    resultJSON2 = self.setupAppleAuthOnMainTenantForTests(appleAuthProv001_CREATE_withAllowCreate, tenantDict['Name'])
    appleAuthProvider = resultJSON2["AuthProviders"][1]

    result2JSON = self.loginWithApple(0, tenantDict['Name'], appleAuthProvider, [200])

    #Turn off auto user creation
    tenantDict2 = self.getTenantDICT(tenantDict['Name'])
    tenantDict2['AllowUserCreation'] = False
    tenantDict3 = self.updateTenant(tenantDict2, [200])

    #Try and login - should not need to create so will succeed
    result3JSON = self.loginWithApple(0, tenantDict['Name'], appleAuthProvider, [200])

  def test_nousercreation_fails(self):
    #Test authentication via apple.
    ## Must use mocks
    tenantDict = self.createTenantWithAuthProvider(
        TestHelperSuperClass.tenantWithNoAuthProviders,
        True,
        TestHelperSuperClass.sampleInternalAuthProv001_CREATE_WithAllowUserCreation
    )

    resultJSON2 = self.setupAppleAuthOnMainTenantForTests(appleAuthProv001_CREATE, tenantDict['Name'])
    appleAuthProvider = resultJSON2["AuthProviders"][1]

    result2JSON = self.loginWithApple(0, tenantDict['Name'], appleAuthProvider, [401])
    self.assertEqual(result2JSON["message"], "authNotFoundException")

  def test_authWithUserCreationAndFrontendSendingUserObject(self):
    #Test authentication via apple.
    ## This does not verify that the user object is saved
    tenantDict = self.createTenantWithAuthProvider(
        TestHelperSuperClass.tenantWithNoAuthProviders,
        True,
        TestHelperSuperClass.sampleInternalAuthProv001_CREATE_WithAllowUserCreation
    )

    resultJSON2 = self.setupAppleAuthOnMainTenantForTests(appleAuthProv001_CREATE_withAllowCreate, tenantDict['Name'])
    appleAuthProvider = resultJSON2["AuthProviders"][1]

    result2JSON = self.loginWithApple(1, tenantDict['Name'], appleAuthProvider, [200])

    #Turn off auto user creation
    tenantDict2 = self.getTenantDICT(tenantDict['Name'])
    tenantDict2['AllowUserCreation'] = False
    tenantDict3 = self.updateTenant(tenantDict2, [200])

    #Try and login - should not need to create so will succeed
    result3JSON = self.loginWithApple(0, tenantDict['Name'], appleAuthProvider, [200])


