#Test helper functions
# defines a baseclass with extra functions
# https://docs.python.org/3/library/unittest.html
import unittest
import json
from appObj import appObj
import copy
import datetime
import pytz
from baseapp_for_restapi_backend_with_swagger import from_iso8601
import jwt
from base64 import b64decode

from tenants import GetTenant, CreateTenant, failedToCreateTenantException, Login, UnknownUserIDException, CreateUser, _getAuthProvider
from constants import masterTenantName, jwtHeaderName, DefaultHasAccountRole, masterTenantDefaultSystemAdminRole
import constants
from persons import CreatePerson
from jwtTokenGeneration import generateJWTToken
from users import associateUserWithPerson

from object_store_abstraction import createObjectStoreInstance

def AddAuth(appObj, tenantName, authProviderGUID, credentialDICT, personGUID, storeConnection):
  auth = _getAuthProvider(appObj, tenantName, authProviderGUID, storeConnection, None).AddAuth(appObj, credentialDICT, personGUID, storeConnection)
  return auth

internalUSerSufix = "@internalDataStore"

httpOrigin = 'http://a.com'

tenantWithNoAuthProviders = {
  "Name": "NewlyCreatedTenantNoAuth",
  "Description": "Tenant with no auth providers",
  "AllowUserCreation": False,
  "AuthProviders": [],
  "JWTCollectionAllowedOriginList": [httpOrigin]
}
sampleInternalAuthProv001_CREATE = {
  "guid": None,
  "Type": "internal",
  "AllowUserCreation": False,
  "AllowLink": False,
  "AllowUnlink": False,
  "LinkText": 'Link',
  "MenuText": "Default Menu Text",
  "IconLink": "string",
  "ConfigJSON": "{\"userSufix\": \"" + internalUSerSufix + "\"}",
  "StaticlyLoadedData": {},
  "saltForPasswordHashing": None
}
sampleInternalAuthProv001_CREATE_WithAllowUserCreation = copy.deepcopy(sampleInternalAuthProv001_CREATE)
sampleInternalAuthProv001_CREATE_WithAllowUserCreation['AllowUserCreation'] = True

env = {
  'APIAPP_MODE': 'DOCKER',
  'APIAPP_JWTSECRET': 'DOsaddsaCKER',
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
  'APIAPP_GATEWAYINTERFACECONFIG': '{"Type": "none"}',
  'APIAPP_DEFAULTMASTERTENANTJWTCOLLECTIONALLOWEDORIGINFIELD': httpOrigin + ', https://b.com, http://c.co.uk'
}

SQLAlchemy_LocalDBConfigDict = {
  "Type":"SQLAlchemy",
  "connectionString":"mysql+pymysql://saas_user_man_user:saas_user_man_testing_password@127.0.0.1:10103/saas_user_man"
}
SQLAlchemy_LocalDBConfigDict_withPrefix = copy.deepcopy(SQLAlchemy_LocalDBConfigDict)
SQLAlchemy_LocalDBConfigDict_withPrefix["objectPrefix"] ="testPrefix"

def get_APIAPP_DEFAULTHOMEADMINPASSWORD_bytes():
  #bytes(password, 'utf-8')
  return bytes(env['APIAPP_DEFAULTHOMEADMINPASSWORD'], 'utf-8')

def getObjectStoreExternalFns():
  return {
    'getCurDateTime': appObj.getCurDateTime,
    'getPaginatedResult': appObj.getPaginatedResult
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

  def sortAllMembers(self, objToSotr):
    if isinstance(objToSotr,list):
      for k in objToSotr:
        self.sortAllMembers(k)
      if len(objToSotr)>1:
        if isinstance(objToSotr[0],dict):
          return #list has dicts inside so no way of sorting
        objToSotr.sort()
      return
    if isinstance(objToSotr,dict):
      for k in objToSotr.keys():
        self.sortAllMembers(objToSotr[k])
      return

  def convertAnyByteValueToString(self, val):
    if isinstance(val,list):
      for a in val:
        self.convertAnyByteValueToString(a)
    if isinstance(val,dict):
      for a in val:
        if isinstance(val[a],bytes):
          #print("CHANGING TO UTF:", val[a])
          val[a] = val[a].decode("utf-8")
        self.convertAnyByteValueToString(val[a])
    else:
      pass

  def areJSONStringsEqual(self, str1, str2):
    self.sortAllMembers(str1)
    self.sortAllMembers(str2)
    self.convertAnyByteValueToString(str1)
    self.convertAnyByteValueToString(str2)
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
    cleaned1 = copy.deepcopy(str1)
    cleaned2 = copy.deepcopy(str2)
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

def getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(username, password, tenantAuthProvSalt):
  masterSecretKey = (username + ":" + password + ":AG44")
  ret = appObj.bcrypt.hashpw(masterSecretKey, b64decode(tenantAuthProvSalt))
  return ret


class testClassWithTestClient(testHelperSuperClass):
  testClient = None
  standardStartupTime = pytz.timezone('Europe/London').localize(datetime.datetime(2018,1,1,13,46,0,0))

  loginAPIPrefix = '/api/public/login'
  adminAPIPrefix = '/api/authed/admin'
  currentAuthAPIPrefix = '/api/authed/currentAuth'

  def _getEnvironment(self):
    raise Exception("Should be overridden")

  def setUp(self):
    # curDatetime = datetime.datetime.now(pytz.utc)
    # for testing always pretend the server started at a set datetime
    self.pre_setUpHook()
    appObj.init(self._getEnvironment(), self.standardStartupTime, testingMode = True)
    self.testClient = appObj.flaskAppObject.test_client()
    self.testClient.testing = True
  def tearDown(self):
    self.testClient = None

  def pre_setUpHook(self):
    pass

  def decodeToken(self, JWTToken):
    return jwt.decode(JWTToken, b64decode(appObj.APIAPP_JWTSECRET), algorithms=['HS256'])
    #return jwt.decode(JWTToken, b64decode(json.loads(env['APIAPP_GATEWAYINTERFACECONFIG'])['jwtSecret']), algorithms=['HS256'])

  def createTwoUsersForOnePerson(self, userID1, userID2, InternalAuthUsername, storeConnection):
    masterTenant = GetTenant(masterTenantName, storeConnection, appObj=appObj)
    CreateUser(appObj, {"user_unique_identifier": userID1, "known_as": userID1}, masterTenantName, "test/createTwoUsersForOnePerson", storeConnection)
    CreateUser(appObj, {"user_unique_identifier": userID2, "known_as": userID2}, masterTenantName, "test/createTwoUsersForOnePerson", storeConnection)
    authProvGUID = list(masterTenant.getAuthProviderGUIDList())[0] #Just use first configured authProvider
    person = CreatePerson(appObj, storeConnection, None, 'a','b','c')
    authData = AddAuth(
      appObj, masterTenantName, authProvGUID, {
        "username": InternalAuthUsername,
        "password": get_APIAPP_DEFAULTHOMEADMINPASSWORD_bytes()
      },
      person['guid'],
      storeConnection
    )
    associateUserWithPerson(appObj, userID1, person['guid'], storeConnection)
    associateUserWithPerson(appObj, userID2, person['guid'], storeConnection)

    return {
      'authProvGUID': authProvGUID,
      'person': person
    }

  def getDefaultHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(self, tenantAuthProvSalt):
    return getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(env['APIAPP_DEFAULTHOMEADMINUSERNAME'], env['APIAPP_DEFAULTHOMEADMINPASSWORD'], tenantAuthProvSalt)

  #Returns a token with the admin user logged in
  def getNormalJWTToken(self):
    userIDForToken = appObj.defaultUserGUID
    return self.makeJWTTokenWithMasterTenantRoles(
      [DefaultHasAccountRole, masterTenantDefaultSystemAdminRole, constants.SecurityEndpointAccessRole],
      userIDForToken
    )


  def makeJWTTokenWithMasterTenantRoles(self, roles, UserID='abc123'):
    userDict = {
      "UserID": UserID,
      "TenantRoles": { masterTenantName: roles}
    }
    return self.generateJWTToken(userDict)


  def generateJWTToken(self, userDict):
    personGUID = appObj.testingDefaultPersonGUID
    return generateJWTToken(appObj, userDict, appObj.APIAPP_JWTSECRET, userDict['UserID'], personGUID, 'DummyCurrentlyAuthedGUID', 'DummyAuthKey')['JWTToken']

  def getTenantDICT(self, tenantName):
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/tenants', headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

    for curTenant in resultJSON['result']:
      if curTenant['Name'] == tenantName:
        return curTenant
    return None

  def createTenantForTesting(self, tenantDICT):
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants',
      headers={ jwtHeaderName: self.getNormalJWTToken()},
      data=json.dumps(tenantDICT),
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 201, result.get_data(as_text=True))
    resultJSON = json.loads(result.get_data(as_text=True))

    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON, tenantDICT, ["ObjectVersion"], msg='JSON of created Tenant is not the same')
    self.assertEqual(resultJSON["ObjectVersion"],"1")

    return resultJSON

  def updateTenant(self, tenantDICT, expectedResults):
    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + tenantDICT['Name'],
      headers={ jwtHeaderName: self.getNormalJWTToken()},
      data=json.dumps(tenantDICT),
      content_type='application/json'
    )
    for x in expectedResults:
        if result.status_code == x:
          return json.loads(result.get_data(as_text=True))
    self.assertTrue(False,msg="Wrong status code returned, expected one of " + str(expectedResults) + " got " + str(result.status_code) + ":" + result.get_data(as_text=True))

  def createTenantForTestingWithMutipleAuthProviders(self, tenantDICT, authProvDictList):
    tenantJSON = self.createTenantForTesting(tenantDICT)
    tenantWithAuthProviders = copy.deepcopy(tenantDICT)
    a = []
    for b in authProvDictList:
      a.append(copy.deepcopy(b))
    tenantWithAuthProviders['AuthProviders'] = a
    tenantWithAuthProviders['ObjectVersion'] = tenantJSON['ObjectVersion']

    return self.updateTenant(tenantWithAuthProviders, [200])

  def createTenantWithAuthProvider(self, tenantBase, tenantUserCreation, authProvDict):
    #This will create a new tenant, add an auth provider and optionally toggle tenant user creation
    tenantWithUserCreation = copy.deepcopy(tenantBase)
    if tenantUserCreation is not None:
      tenantWithUserCreation['AllowUserCreation'] = tenantUserCreation
    authProvCreateWithUserCreation = copy.deepcopy(authProvDict) #sampleInternalAuthProv001_CREATE sampleInternalAuthProv001_CREATE_WithAllowUserCreation
    return self.createTenantForTestingWithMutipleAuthProviders(tenantWithUserCreation, [authProvCreateWithUserCreation])

  def getTenantSpercificAuthProvDict(self, tenant, type):
    result = self.testClient.get(
      self.loginAPIPrefix + '/' + tenant + '/authproviders',
      headers={"Origin": httpOrigin}
    )
    self.assertEqual(result.status_code, 200, msg="Get auth providers service call failed")
    resultJSON = json.loads(result.get_data(as_text=True))
    for x in resultJSON[ 'AuthProviders' ]:
      if x['Type'] == type:
        return x
    raise Exception("Could not find " + str(type) + " auth provider in tenant " + str(tenant))

  def getTenantInternalAuthProvDict(self, tenant):
    return self.getTenantSpercificAuthProvDict(tenant, 'internal')

  def registerInternalUser(self, tenantName, username, password, authProvider):
    hashedPassword = getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(
      username,
      password,
      authProvider['saltForPasswordHashing']
    )
    registerJSON = {
      "authProviderGUID": authProvider['guid'],
      "credentialJSON": {
        "username": username,
        "password": hashedPassword
       }
    }
    registerResult = self.testClient.put(
      self.loginAPIPrefix + '/' + tenantName + '/register',
      data=json.dumps(registerJSON),
      content_type='application/json',
      headers={"Origin": httpOrigin}
    )
    self.assertEqual(registerResult.status_code, 201, msg="Registration failed - " + registerResult.get_data(as_text=True))
    return json.loads(registerResult.get_data(as_text=True))

  def loginAsDefaultUser(self):
    return self.loginAsUser(masterTenantName, self.getTenantInternalAuthProvDict(masterTenantName), env['APIAPP_DEFAULTHOMEADMINUSERNAME'], env['APIAPP_DEFAULTHOMEADMINPASSWORD'])

  def loginAsUser(self, tenant, authProviderDICT, username, password, expectedResults = [200]):
    hashedPassword = getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(
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

  def getNewAuthDICT(self, userName="testUsername"):
    masterTenant = self.getTenantDICT(masterTenantName)

    hashedpassword = getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(
      userName,
      env['APIAPP_DEFAULTHOMEADMINPASSWORD'],
      masterTenant["AuthProviders"][0]["saltForPasswordHashing"]
    )

    newAuthDICT = {
      "personGUID": "FORCED-CONSTANT-TESTING-PERSON-GUID",
      "tenantName": masterTenantName,
      "authProviderGUID": masterTenant["AuthProviders"][0]["guid"],
      "credentialJSON": {
        "username": userName,
        "password": hashedpassword
      }
    }
    return copy.deepcopy(newAuthDICT)


#helper class with setup for an APIClient
class testHelperAPIClient(testClassWithTestClient):
  def _getEnvironment(self):
    return env

import os
SKIPSQLALCHEMYTESTS=False
if ('SKIPSQLALCHEMYTESTS' in os.environ):
  if os.environ["SKIPSQLALCHEMYTESTS"]=="Y":
    SKIPSQLALCHEMYTESTS=True

envUsingDevDatabase = copy.deepcopy(env)
envUsingDevDatabase['APIAPP_OBJECTSTORECONFIG']='{"Type":"SQLAlchemy","connectionString":"mysql+pymysql://saas_user_man_user:saas_user_man_testing_password@127.0.0.1:10103/saas_user_man"}'

class testHelperAPIClientUsingSQLAlchemy(testClassWithTestClient):
  def pre_setUpHook(self):
    if SKIPSQLALCHEMYTESTS:
      print("Skipping SQLAlchemyTests")
      return
    #App object isn't instalised so we need to make an object to reset the data for the test
    fns = {
      'getCurDateTime': appObj.getCurDateTime,
      'getPaginatedResult': appObj.getPaginatedResult
    }
    objectStore = createObjectStoreInstance(json.loads(self._getEnvironment()['APIAPP_OBJECTSTORECONFIG']), fns)
    objectStore.resetDataForTest()

  def _getEnvironment(self):
    if SKIPSQLALCHEMYTESTS:
      return env
    return envUsingDevDatabase

kongISS = "saas_kong_iss"
envUsingKongGateway = copy.deepcopy(env)
envUsingKongGateway['APIAPP_GATEWAYINTERFACECONFIG']='{"Type": "kong", "kongISS": "' + kongISS + '"}'

class testHelperAPIClientUsingKongStaticGateway(testClassWithTestClient):
  def _getEnvironment(self):
    return envUsingKongGateway
