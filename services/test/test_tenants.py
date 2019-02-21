from TestHelperSuperClass import testHelperAPIClient, env, get_APIAPP_DEFAULTHOMEADMINPASSWORD_bytes
from tenants import GetTenant, CreateTenant, failedToCreateTenantException, Login, UnknownIdentityException, CreateUser, _getAuthProvider
from constants import masterTenantName, masterTenantDefaultDescription, masterTenantDefaultAuthProviderMenuText, masterTenantDefaultAuthProviderMenuIconLink, masterTenantDefaultSystemAdminRole, DefaultHasAccountRole
from appObj import appObj
from constants import authFailedException
from person import CreatePerson, associatePersonWithAuth
import json
from base64 import b64decode
from users import associateUserWithPerson

def AddAuth(appObj, tenantName, authProviderGUID, credentialDICT, personGUID):
  auth = _getAuthProvider(appObj, tenantName, authProviderGUID).AddAuth(appObj, credentialDICT, personGUID)
  return auth

class test_tenants(testHelperAPIClient):

#Actual tests below

  def test_cantCreateTenantWithSameNameAsMaster(self):
    with self.assertRaises(Exception) as context:
      tenant = CreateTenant(appObj, masterTenantName)
    self.checkGotRightException(context,failedToCreateTenantException)


  def test_MasterTenantExists(self):
    masterTenant = GetTenant(appObj,masterTenantName)
    self.assertFalse(masterTenant is None, msg="Master Tenant was not created")
    self.assertEquals(masterTenant.getJSONRepresenation()['Name'], masterTenantName, msg="Master tenant name is wrong")
    self.assertEquals(masterTenant.getJSONRepresenation()['Description'], masterTenantDefaultDescription, msg="Master tenant default description wrong")
    self.assertFalse(masterTenant.getJSONRepresenation()['AllowUserCreation'], msg="Master tenant defaults to allowing user creation")

    #Check AuthProvider is correct
    expectedAuthProviderJSON = {
      "guid": "ignored",
      "MenuText": masterTenantDefaultAuthProviderMenuText,
      "IconLink": masterTenantDefaultAuthProviderMenuIconLink,
      "Type":  "internal",
      "AllowUserCreation": False,
      "ConfigJSON": {
        "userSufix": "@internalDataStore"
      }
    }
    self.assertEqual(masterTenant.getNumberOfAuthProviders(),1, msg="No internal Auth Providers found")
    singleAuthProvGUID = ""
    for guid in masterTenant.getAuthProviderGUIDList():
      singleAuthProvGUID=guid

    self.assertJSONStringsEqualWithIgnoredKeys(masterTenant.getAuthProvider(singleAuthProvGUID), expectedAuthProviderJSON, ['guid','saltForPasswordHashing'], msg="Internal Auth Provider default data incorrect")

    #Check initial user has been created and we could log in
    UserIDandRoles = Login(appObj, masterTenantName, singleAuthProvGUID, {
      'username': env['APIAPP_DEFAULTHOMEADMINUSERNAME'],
      'password': bytes(self.getDefaultHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(masterTenant.getAuthProvider(singleAuthProvGUID)['saltForPasswordHashing']),'utf-8')
    })
    #An exception is raised if the login fails
    expectedRoles = {
      "UserID": 'somerandomguid',
      "TenantRoles": {
        "usersystem": [masterTenantDefaultSystemAdminRole, DefaultHasAccountRole]
       },
       "authedPersonGuid": "Ignore",
      "known_as": env['APIAPP_DEFAULTHOMEADMINUSERNAME'],
      "other_data": {}
    }
    self.assertJSONStringsEqualWithIgnoredKeys(self.decodeToken(UserIDandRoles['jwtData']['JWTToken']), expectedRoles, ['UserID', 'exp', 'iss', 'authedPersonGuid'], msg="Returned roles incorrect")
    
  def test_StandardUserInvalidPassword(self):
    masterTenant = GetTenant(appObj,masterTenantName)
    self.assertEqual(masterTenant.getNumberOfAuthProviders(),1, msg="No internal Auth Providers found")
    singleAuthProvGUID = ""
    for guid in masterTenant.getAuthProviderGUIDList():
      singleAuthProvGUID=guid

    with self.assertRaises(Exception) as context:
      UserIDandRoles = Login(appObj, masterTenantName, singleAuthProvGUID, {
        'username': env['APIAPP_DEFAULTHOMEADMINUSERNAME'],
        'password': bytes(env['APIAPP_DEFAULTHOMEADMINPASSWORD'] + 'Extra bit to make password wrong','utf-8')
      })
    self.checkGotRightException(context,authFailedException)

  def test_StandardUserInvalidUsername(self):
    masterTenant = GetTenant(appObj,masterTenantName)
    self.assertEqual(masterTenant.getNumberOfAuthProviders(),1, msg="No internal Auth Providers found")
    singleAuthProvGUID = ""
    for guid in masterTenant.getAuthProviderGUIDList():
      singleAuthProvGUID=guid

    with self.assertRaises(Exception) as context:
      UserIDandRoles = Login(appObj, masterTenantName, singleAuthProvGUID, {
        'username': env['APIAPP_DEFAULTHOMEADMINUSERNAME'] + 'Extra bit to make username wrong',
        'password': get_APIAPP_DEFAULTHOMEADMINPASSWORD_bytes()
      })
    self.checkGotRightException(context,authFailedException)

  def test_StandardUserLoginToInvalidIdentity(self):
    masterTenant = GetTenant(appObj,masterTenantName)
    self.assertEqual(masterTenant.getNumberOfAuthProviders(),1, msg="No internal Auth Providers found")
    singleAuthProvGUID = ""
    for guid in masterTenant.getAuthProviderGUIDList():
      singleAuthProvGUID=guid
      

    with self.assertRaises(Exception) as context:
      UserIDandRoles = Login(appObj, masterTenantName, singleAuthProvGUID, {
        'username': env['APIAPP_DEFAULTHOMEADMINUSERNAME'],
        'password': bytes(self.getDefaultHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(masterTenant.getAuthProvider(singleAuthProvGUID)['saltForPasswordHashing']),'utf-8')
      }, 'invalid_identity_guid')
    self.checkGotRightException(context,UnknownIdentityException)

  # Person can log in and choose to use userA or userB
  def test_oneAuthCanAccessTwoIdentities(self):
    userID1 = 'TestUser1'
    userID2 = 'TestUser2'
    InternalAuthUsername = 'ABC'
    res = self.createUserWithTwoIdentititesForOnePerson(userID1, userID2, InternalAuthUsername)
    
    #Login and get list of identities
    UserIDandRoles = Login(appObj, masterTenantName, res['authProvGUID'], {
      'username': InternalAuthUsername,
      'password': get_APIAPP_DEFAULTHOMEADMINPASSWORD_bytes()
    })
    foundIdentity1 = False
    foundIdentity2 = False
    print("test_oneAuthCanAccessTwoIdentities UserIDandRoles:",UserIDandRoles)
    for curUserID in UserIDandRoles['possibleUserIDs']:
      if userID1 == curUserID:
        foundIdentity1 = True
      if userID2 == curUserID:
        foundIdentity2 = True
    self.assertTrue(foundIdentity1, msg="Identity 1 was not returned when list of login identities to use was given")
    self.assertTrue(foundIdentity2, msg="Identity 2 was not returned when list of login identities to use was given")
    
    #Try and log in using identities
    UserIDandRoles = Login(appObj, masterTenantName, res['authProvGUID'], {
      'username': InternalAuthUsername,
      'password': get_APIAPP_DEFAULTHOMEADMINPASSWORD_bytes()
    }, userID1)
    expectedJSONResponse = {
      'TenantRoles': {"usersystem": ["hasaccount"]}, 
      'UserID': userID1, 
      "exp": "xx", 
      "iss": userID1,
      "authedPersonGuid": res['person']['guid'],
      "known_as": userID1,
      "other_data": {}
    }
    self.assertJSONStringsEqualWithIgnoredKeys(self.decodeToken(UserIDandRoles['jwtData']['JWTToken']), expectedJSONResponse, ['exp'], msg="Failed to login to identity 1")
    
    UserIDandRoles = Login(appObj, masterTenantName, res['authProvGUID'], {
      'username': InternalAuthUsername,
      'password': get_APIAPP_DEFAULTHOMEADMINPASSWORD_bytes()
    }, userID2)
    expectedJSONResponse = {
      'TenantRoles': {"usersystem": ["hasaccount"]}, 
      'UserID': userID2, 
      "exp": "xx", 
      "iss": userID2,
      "authedPersonGuid": res['person']['guid'],
      "known_as": userID2,
      "other_data": {}
    }
    self.assertJSONStringsEqualWithIgnoredKeys(self.decodeToken(UserIDandRoles['jwtData']['JWTToken']), expectedJSONResponse, ['exp'], msg="Failed to login to identity 2")


  #UserA can be shared by many People (Who may or may not have many auths)
  def test_oneUserCanBeAccessedByTwoAuths(self):
    masterTenant = GetTenant(appObj,masterTenantName)
    userID = 'TestUser'
    CreateUser(appObj, {"user_unique_identifier": userID, "known_as": userID}, masterTenantName)

    authProvGUID = list(masterTenant.getAuthProviderGUIDList())[0] #Just use first configured authProvider
    person1 = CreatePerson(appObj)
    person2 = CreatePerson(appObj)
    InternalAuthUsername1 = 'SomeLogin1'
    InternalAuthUsername2 = 'SomeLogin2'
    authData1 = AddAuth(appObj, masterTenantName, authProvGUID, {
      "username": InternalAuthUsername1, 
      "password": get_APIAPP_DEFAULTHOMEADMINPASSWORD_bytes()
    },
    person1['guid'])
    authData2 = AddAuth(appObj, masterTenantName, authProvGUID, {
      "username": InternalAuthUsername2, 
      "password": get_APIAPP_DEFAULTHOMEADMINPASSWORD_bytes()
    },
    person2['guid'])
    associateUserWithPerson(appObj, userID, person1['guid'])
    associateUserWithPerson(appObj, userID, person2['guid'])

    #Try and log in and make sure both people get access to the user
    UserIDandRoles = Login(appObj, masterTenantName, authProvGUID, {
      'username': InternalAuthUsername1,
      'password': get_APIAPP_DEFAULTHOMEADMINPASSWORD_bytes()
    })
    expectedJSONResponse = {
      'TenantRoles': {"usersystem": ["hasaccount"]}, 
      'UserID': userID, 
      "exp": "xx", 
      "iss": userID,
      "authedPersonGuid": person1['guid'],
      "known_as": userID,
      "other_data": {}
    }
    self.assertJSONStringsEqualWithIgnoredKeys(self.decodeToken(UserIDandRoles['jwtData']['JWTToken']), expectedJSONResponse, ['exp'], msg="Failed to login to identity 1")
    
    UserIDandRoles = Login(appObj, masterTenantName, authProvGUID, {
      'username': InternalAuthUsername2,
      'password': get_APIAPP_DEFAULTHOMEADMINPASSWORD_bytes()
    })
    expectedJSONResponse['authedPersonGuid'] = person2['guid']
    self.assertJSONStringsEqualWithIgnoredKeys(self.decodeToken(UserIDandRoles['jwtData']['JWTToken']), expectedJSONResponse, ['exp'], msg="Failed to login to identity 2")

