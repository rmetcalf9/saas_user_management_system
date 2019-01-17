#Test helper functions
# defines a baseclass with extra functions
# https://docs.python.org/3/library/unittest.html
import unittest
import json
from appObj import appObj

import datetime
import pytz
from baseapp_for_restapi_backend_with_swagger import from_iso8601
import jwt
from base64 import b64decode

from tenants import GetTenant, CreateTenant, failedToCreateTenantException, Login, UnknownIdentityException, CreateUser, createNewIdentity, AddAuth, associateIdentityWithPerson
from constants import masterTenantName
from person import CreatePerson, associatePersonWithAuth

env = {
  'APIAPP_MODE': 'DOCKER',
  'APIAPP_VERSION': 'TEST-3.3.3',
  'APIAPP_FRONTEND': '_',
  'APIAPP_APIURL': 'http://apiurlxxx',
  'APIAPP_FRONTENDURL': 'http://frontenddummytestxxx',
  'APIAPP_APIACCESSSECURITY': '[{ "type": "basic-auth" }]',
  'APIAPP_MASTERPASSWORDFORPASSHASH': 'TestPPP',
  'APIAPP_DEFAULTHOMEADMINUSERNAME': 'AdminTestSet',
  'APIAPP_DEFAULTHOMEADMINPASSWORD': 'sadfdsfdsf4325g...ds',
  'APIAPP_JWT_TOKEN_TIMEOUT': '60',
  'APIAPP_REFRESH_TOKEN_TIMEOUT': '240',
  'APIAPP_REFRESH_SESSION_TIMEOUT': '2400',
  'APIAPP_GATEWAYINTERFACETYPE': 'none',
  'APIAPP_GATEWAYINTERFACECONFIG': '{"jwtSecret":"some_secretxx"}'
}

class testHelperSuperClass(unittest.TestCase):
  def checkGotRightException(self, context, ExpectedException):
    if (context.exception != None):
      if (context.exception != ExpectedException):
        print("**** Wrong exception raised:")
        print("      expected: " + type(ExpectedException).__name__ + ' - ' + str(ExpectedException));
        print("           got: " + type(context.exception).__name__ + ' - ' + str(context.exception));
        raise context.exception
    self.assertTrue(ExpectedException == context.exception)

  def areJSONStringsEqual(self, str1, str2):
    a = json.dumps(str1, sort_keys=True)
    b = json.dumps(str2, sort_keys=True)
    return (a == b)

  def assertJSONStringsEqual(self, str1, str2, msg=''):
    if (self.areJSONStringsEqual(str1,str2)):
      return
    print("Mismatch JSON")
    a = json.dumps(str1, sort_keys=True)
    b = json.dumps(str2, sort_keys=True)
    print(a)
    print("--")
    print(b)
    self.assertTrue(False, msg=msg)
    
  #provide a list of ignored keys
  def assertJSONStringsEqualWithIgnoredKeys(self, str1, str2, ignoredKeys, msg=''):
    cleaned1 = str1.copy()
    cleaned2 = str2.copy()
    for key_to_ignore in ignoredKeys:
      keyPresentInEither = False
      if key_to_ignore in cleaned1:
        keyPresentInEither = True
      if key_to_ignore in cleaned2:
        keyPresentInEither = True
      if keyPresentInEither:
        cleaned1[key_to_ignore] = 'ignored'
        cleaned2[key_to_ignore] = 'ignored'
    return self.assertJSONStringsEqual(cleaned1, cleaned2, msg)

  def assertTimeCloseToCurrent(self, time, msg='Creation time is more than 3 seconds adrift'):
    if (isinstance(time, str)):
      time = from_iso8601(time)
    curTime = datetime.datetime.now(pytz.timezone("UTC"))
    time_diff = (curTime - time).total_seconds()
    self.assertTrue(time_diff < 3, msg=msg)

  def assertResponseCodeEqual(self, result, expectedResponse, msg=''):
    if result.status_code==expectedResponse:
      return
    print(result.get_data(as_text=True))
    self.assertEqual(result.status_code, expectedResponse, msg)
    
#helper class with setup for an APIClient
class testHelperAPIClient(testHelperSuperClass):
  testClient = None
  standardStartupTime = pytz.timezone('Europe/London').localize(datetime.datetime(2018,1,1,13,46,0,0))

  def setUp(self):
    # curDatetime = datetime.datetime.now(pytz.utc)
    # for testing always pretend the server started at a set datetime
    appObj.init(env, self.standardStartupTime, testingMode = True)
    self.testClient = appObj.flaskAppObject.test_client()
    self.testClient.testing = True 
  def tearDown(self):
    self.testClient = None

  def decodeToken(self, JWTToken): 
    return jwt.decode(JWTToken, b64decode(json.loads(env['APIAPP_GATEWAYINTERFACECONFIG'])['jwtSecret']), algorithms=['HS256'])

  def createUserWithTwoIdentititesForOneUser(self, userID1, userID2, InternalAuthUsername):
    masterTenant = GetTenant(appObj,masterTenantName)
    CreateUser(appObj, userID1)
    CreateUser(appObj, userID2)
    identity1 = createNewIdentity(appObj, 'standard','standard', userID1)
    identity2 = createNewIdentity(appObj, 'standard','standard', userID2)
    authProvGUID = list(masterTenant.getAuthProviderGUIDList())[0] #Just use first configured authProvider
    person = CreatePerson(appObj)
    authData = AddAuth(appObj, masterTenantName, authProvGUID, {
      "username": InternalAuthUsername, 
      "password": appObj.APIAPP_DEFAULTHOMEADMINPASSWORD
    },
    person['guid'])
    associatePersonWithAuth(appObj, person['guid'], authData['AuthUserKey'])
    associateIdentityWithPerson(appObj, identity1['guid'], person['guid'])
    associateIdentityWithPerson(appObj, identity2['guid'], person['guid'])
    
    return {
      'authProvGUID': authProvGUID,
      'identity1': identity1,
      'identity2': identity2,
      'person': person
    }

  def getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(self, username, password, tenantAuthProvSalt):
    masterSecretKey = (username + ":" + password + ":AG44")
    return appObj.bcrypt.hashpw(masterSecretKey, b64decode(tenantAuthProvSalt))
  def getDefaultHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(self, tenantAuthProvSalt):
    return self.getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(env['APIAPP_DEFAULTHOMEADMINUSERNAME'], env['APIAPP_DEFAULTHOMEADMINPASSWORD'], tenantAuthProvSalt)

