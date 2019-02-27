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

from tenants import GetTenant, CreateTenant, failedToCreateTenantException, Login, UnknownIdentityException, CreateUser, _getAuthProvider
from constants import masterTenantName, jwtHeaderName, DefaultHasAccountRole, masterTenantDefaultSystemAdminRole
from persons import CreatePerson
from jwtTokenGeneration import generateJWTToken
from users import associateUserWithPerson

def AddAuth(appObj, tenantName, authProviderGUID, credentialDICT, personGUID):
  auth = _getAuthProvider(appObj, tenantName, authProviderGUID).AddAuth(appObj, credentialDICT, personGUID)
  return auth

internalUSerSufix = "@internalDataStore"

tenantWithNoAuthProviders = {
  "Name": "NewlyCreatedTenantNoAuth",
  "Description": "Tenant with no auth providers",
  "AllowUserCreation": False,
  "AuthProviders": []
}
sampleInternalAuthProv001_CREATE = {
  "guid": None,
  "Type": "internal",
  "AllowUserCreation": False,
  "MenuText": "Default Menu Text",
  "IconLink": "string",
  "ConfigJSON": "{\"userSufix\": \"" + internalUSerSufix + "\"}",
  "saltForPasswordHashing": None
} 



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

def get_APIAPP_DEFAULTHOMEADMINPASSWORD_bytes():
  #bytes(password, 'utf-8')
  return bytes(env['APIAPP_DEFAULTHOMEADMINPASSWORD'], 'utf-8')


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

def getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(username, password, tenantAuthProvSalt):
  masterSecretKey = (username + ":" + password + ":AG44")
  ret = appObj.bcrypt.hashpw(masterSecretKey, b64decode(tenantAuthProvSalt))
  return ret

    
#helper class with setup for an APIClient
class testHelperAPIClient(testHelperSuperClass):
  testClient = None
  standardStartupTime = pytz.timezone('Europe/London').localize(datetime.datetime(2018,1,1,13,46,0,0))

  loginAPIPrefix = '/api/public/login'
  adminAPIPrefix = '/api/authed/admin'

  
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

  def createTwoUsersForOnePerson(self, userID1, userID2, InternalAuthUsername):
    masterTenant = GetTenant(appObj,masterTenantName)
    CreateUser(appObj, {"user_unique_identifier": userID1, "known_as": userID1}, masterTenantName, "test/createTwoUsersForOnePerson")
    CreateUser(appObj, {"user_unique_identifier": userID2, "known_as": userID2}, masterTenantName, "test/createTwoUsersForOnePerson")
    authProvGUID = list(masterTenant.getAuthProviderGUIDList())[0] #Just use first configured authProvider
    person = CreatePerson(appObj)
    authData = AddAuth(appObj, masterTenantName, authProvGUID, {
      "username": InternalAuthUsername, 
      "password": get_APIAPP_DEFAULTHOMEADMINPASSWORD_bytes()
    },
    person['guid'])
    associateUserWithPerson(appObj, userID1, person['guid'])
    associateUserWithPerson(appObj, userID2, person['guid'])
    
    return {
      'authProvGUID': authProvGUID,
      'person': person
    }

  def getDefaultHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(self, tenantAuthProvSalt):
    return getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(env['APIAPP_DEFAULTHOMEADMINUSERNAME'], env['APIAPP_DEFAULTHOMEADMINPASSWORD'], tenantAuthProvSalt)

  #Returns a token with the admin user logged in
  def getNormalJWTToken(self):
    userIDForToken = appObj.defaultUserGUID
    return self.makeJWTTokenWithMasterTenantRoles([DefaultHasAccountRole, masterTenantDefaultSystemAdminRole], userIDForToken)
  
  
  def makeJWTTokenWithMasterTenantRoles(self, roles, UserID='abc123'):
    userDict = {
      "UserID": UserID,
      "TenantRoles": { masterTenantName: roles}
    }
    return self.generateJWTToken(userDict)


  def generateJWTToken(self, userDict):
    jwtSecretAndKey = {
      'secret': appObj.gateway.GetJWTTokenSecret(userDict['UserID']),
      'key': userDict['UserID']
    }
    personGUID = appObj.testingDefaultPersonGUID
    return generateJWTToken(appObj, userDict, jwtSecretAndKey, personGUID)['JWTToken']
    
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
    
  def createTenantForTestingWithMutipleAuthProviders(self, tenantDICT, authProvDictList):
    tenantJSON = self.createTenantForTesting(tenantDICT)
    tenantWithAuthProviders = copy.deepcopy(tenantDICT)
    a = []
    for b in authProvDictList:
      a.append(copy.deepcopy(b))
    tenantWithAuthProviders['AuthProviders'] = a
    tenantWithAuthProviders['ObjectVersion'] = tenantJSON['ObjectVersion']
    
    #print("tenantJSON:",tenantJSON)
    #print("tenantWithAuthProviders:",tenantWithAuthProviders)
    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + tenantWithAuthProviders['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantWithAuthProviders), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 200)
    return json.loads(result.get_data(as_text=True))

  def setupTenantForTesting(self, tenantBase, tenantUserCreation, AuthUserCreation):
    tenantWithUserCreation = copy.deepcopy(tenantBase)
    tenantWithUserCreation['AllowUserCreation'] = tenantUserCreation
    authProvCreateWithUserCreation = copy.deepcopy(sampleInternalAuthProv001_CREATE)
    authProvCreateWithUserCreation['AllowUserCreation'] = AuthUserCreation
    return self.createTenantForTestingWithMutipleAuthProviders(tenantWithUserCreation, [authProvCreateWithUserCreation])

