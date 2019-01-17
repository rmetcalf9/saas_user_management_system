from TestHelperSuperClass import testHelperAPIClient, env
from tenants import GetTenant, CreateTenant, failedToCreateTenantException, Login, UnknownIdentityException, CreateUser, createNewIdentity, AddAuth, associateIdentityWithPerson
from constants import masterTenantName, masterTenantDefaultDescription, masterTenantDefaultAuthProviderMenuText, masterTenantDefaultAuthProviderMenuIconLink, masterTenantDefaultSystemAdminRole, DefaultHasAccountRole
from appObj import appObj
from constants import authFailedException
from person import CreatePerson, associatePersonWithAuth
import json
from base64 import b64decode

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
      'password': self.getDefaultHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(masterTenant.getAuthProvider(singleAuthProvGUID)['saltForPasswordHashing'])
    })
    #An exception is raised if the login fails
    expectedRoles = {
      "UserID": 'somerandomguid',
      "TenantRoles": {
        "usersystem": [masterTenantDefaultSystemAdminRole, DefaultHasAccountRole]
       },
       "authedPersonGuid": "Ignore"
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
        'password': env['APIAPP_DEFAULTHOMEADMINPASSWORD'] + 'Extra bit to make password wrong'
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
        'password': env['APIAPP_DEFAULTHOMEADMINPASSWORD']
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
        'password': self.getDefaultHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(masterTenant.getAuthProvider(singleAuthProvGUID)['saltForPasswordHashing'])
      }, 'invalid_identity_guid')
    self.checkGotRightException(context,UnknownIdentityException)

  # Person can log in and choose to use userA or userB
  def test_oneAuthCanAccessTwoIdentities(self):
    userID1 = 'TestUser1'
    userID2 = 'TestUser2'
    InternalAuthUsername = 'ABC'
    res = self.createUserWithTwoIdentititesForOneUser(userID1, userID2, InternalAuthUsername)
    
    #Login and get list of identities
    UserIDandRoles = Login(appObj, masterTenantName, res['authProvGUID'], {
      'username': InternalAuthUsername,
      'password': appObj.APIAPP_DEFAULTHOMEADMINPASSWORD
    })
    foundIdentity1 = False
    foundIdentity2 = False
    for curIdentity in UserIDandRoles['possibleIdentities'].keys():
      if res['identity1']['guid'] == UserIDandRoles['possibleIdentities'][curIdentity]['guid']:
        foundIdentity1 = True
      if res['identity2']['guid'] == UserIDandRoles['possibleIdentities'][curIdentity]['guid']:
        foundIdentity2 = True
    self.assertTrue(foundIdentity1, msg="Identity 1 was not returned when list of login identities to use was given")
    self.assertTrue(foundIdentity2, msg="Identity 2 was not returned when list of login identities to use was given")
    
    #Try and log in using identities
    UserIDandRoles = Login(appObj, masterTenantName, res['authProvGUID'], {
      'username': InternalAuthUsername,
      'password': appObj.APIAPP_DEFAULTHOMEADMINPASSWORD
    }, res['identity1']['guid'])
    expectedJSONResponse = {
      'TenantRoles': {}, 
      'UserID': userID1, 
      "exp": "xx", 
      "iss": "_CheckUserInitAndReturnJWTSecretAndKey_key",
      "authedPersonGuid": res['person']['guid']
    }
    self.assertJSONStringsEqualWithIgnoredKeys(self.decodeToken(UserIDandRoles['jwtData']['JWTToken']), expectedJSONResponse, ['exp'], msg="Failed to login to identity 1")
    
    UserIDandRoles = Login(appObj, masterTenantName, res['authProvGUID'], {
      'username': InternalAuthUsername,
      'password': appObj.APIAPP_DEFAULTHOMEADMINPASSWORD
    }, res['identity2']['guid'])
    expectedJSONResponse = {
      'TenantRoles': {}, 
      'UserID': userID2, 
      "exp": "xx", 
      "iss": "_CheckUserInitAndReturnJWTSecretAndKey_key",
      "authedPersonGuid": res['person']['guid']
    }
    self.assertJSONStringsEqualWithIgnoredKeys(self.decodeToken(UserIDandRoles['jwtData']['JWTToken']), expectedJSONResponse, ['exp'], msg="Failed to login to identity 1")


  #UserA can be shared by many People (Who may or may not have many auths)
  def test_oneUserCanBeAccessedByTwoAuths(self):
    masterTenant = GetTenant(appObj,masterTenantName)
    userID = 'TestUser'
    CreateUser(appObj, userID)
    identity = createNewIdentity(appObj, 'standard','standard', userID)

    authProvGUID = list(masterTenant.getAuthProviderGUIDList())[0] #Just use first configured authProvider
    person1 = CreatePerson(appObj)
    person2 = CreatePerson(appObj)
    InternalAuthUsername1 = 'SomeLogin1'
    InternalAuthUsername2 = 'SomeLogin2'
    authData1 = AddAuth(appObj, masterTenantName, authProvGUID, {
      "username": InternalAuthUsername1, 
      "password": appObj.APIAPP_DEFAULTHOMEADMINPASSWORD
    },
    person1['guid'])
    authData2 = AddAuth(appObj, masterTenantName, authProvGUID, {
      "username": InternalAuthUsername2, 
      "password": appObj.APIAPP_DEFAULTHOMEADMINPASSWORD
    },
    person2['guid'])
    associateIdentityWithPerson(appObj, identity['guid'], person1['guid'])
    associateIdentityWithPerson(appObj, identity['guid'], person2['guid'])

    #Try and log in and make sure both people get access to the user
    UserIDandRoles = Login(appObj, masterTenantName, authProvGUID, {
      'username': InternalAuthUsername1,
      'password': appObj.APIAPP_DEFAULTHOMEADMINPASSWORD
    })
    expectedJSONResponse = {
      'TenantRoles': {}, 
      'UserID': userID, 
      "exp": "xx", 
      "iss": "_CheckUserInitAndReturnJWTSecretAndKey_key",
      "authedPersonGuid": person1['guid']
    }
    self.assertJSONStringsEqualWithIgnoredKeys(self.decodeToken(UserIDandRoles['jwtData']['JWTToken']), expectedJSONResponse, ['exp'], msg="Failed to login to identity 1")
    
    UserIDandRoles = Login(appObj, masterTenantName, authProvGUID, {
      'username': InternalAuthUsername2,
      'password': appObj.APIAPP_DEFAULTHOMEADMINPASSWORD
    })
    expectedJSONResponse['authedPersonGuid'] = person2['guid']
    self.assertJSONStringsEqualWithIgnoredKeys(self.decodeToken(UserIDandRoles['jwtData']['JWTToken']), expectedJSONResponse, ['exp'], msg="Failed to login to identity 2")

