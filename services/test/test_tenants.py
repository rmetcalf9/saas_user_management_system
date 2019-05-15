from TestHelperSuperClass import testHelperAPIClient, env, get_APIAPP_DEFAULTHOMEADMINPASSWORD_bytes
from tenants import GetTenant, CreateTenant, failedToCreateTenantException, Login, UnknownUserIDException, CreateUser, _getAuthProvider
from constants import masterTenantName, masterTenantDefaultDescription, masterTenantDefaultAuthProviderMenuText, masterTenantDefaultAuthProviderMenuIconLink, masterTenantDefaultSystemAdminRole, DefaultHasAccountRole
import constants
from appObj import appObj
from constants import authFailedException
from persons import CreatePerson
import json
from base64 import b64decode
from users import associateUserWithPerson

def AddAuth(appObj, tenantName, authProviderGUID, credentialDICT, personGUID, storeConnection):
  auth = _getAuthProvider(appObj, tenantName, authProviderGUID, storeConnection, None).AddAuth(appObj, credentialDICT, personGUID, storeConnection)
  return auth

class test_tenants(testHelperAPIClient):

#Actual tests below

  def test_cantCreateTenantWithSameNameAsMaster(self):
    def dbfn(storeConnection):
      with self.assertRaises(Exception) as context:
        tenant = CreateTenant(appObj, masterTenantName, "", False, storeConnection, 'a','b','c')
      self.checkGotRightException(context,failedToCreateTenantException)

    appObj.objectStore.executeInsideConnectionContext(dbfn)


  def test_MasterTenantExists(self):
    def someFn(connectionContext):    
      masterTenant = GetTenant(masterTenantName, connectionContext, 'a','b','c')
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
        "AllowLink": False,
        "AllowUnlink": False,
        "LinkText": constants.masterTenantDefaultAuthProviderMenuTextInternalAuthLinkText,
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
      }, 
          None, #requestedUserID
          connectionContext,
          'a','b','c')
      #An exception is raised if the login fails
      expectedRoles = {
        "UserID": 'somerandomguid',
        "TenantRoles": {
          "usersystem": [masterTenantDefaultSystemAdminRole, constants.SecurityEndpointAccessRole, DefaultHasAccountRole]
         },
         "authedPersonGuid": "Ignore",
        "known_as": env['APIAPP_DEFAULTHOMEADMINUSERNAME'],
        "other_data": {
          "createdBy": "init/CreateMasterTenant"
        },
        "currentlyUsedAuthKey": "AdminTestSet@internalDataStore_`@\\/'internal"
      }
      self.assertJSONStringsEqualWithIgnoredKeys(self.decodeToken(UserIDandRoles['jwtData']['JWTToken']), expectedRoles, ['currentlyUsedAuthProviderGuid', 'UserID', 'exp', 'iss', 'authedPersonGuid','associatedPersons'], msg="Returned roles incorrect")
    appObj.objectStore.executeInsideTransaction(someFn)

  def test_StandardUserInvalidPassword(self):
    def someFn(connectionContext):    
      masterTenant = GetTenant(masterTenantName, connectionContext, 'a','b','c')
      self.assertEqual(masterTenant.getNumberOfAuthProviders(),1, msg="No internal Auth Providers found")
      singleAuthProvGUID = ""
      for guid in masterTenant.getAuthProviderGUIDList():
        singleAuthProvGUID=guid

      with self.assertRaises(Exception) as context:
        UserIDandRoles = Login(appObj, masterTenantName, singleAuthProvGUID, {
          'username': env['APIAPP_DEFAULTHOMEADMINUSERNAME'],
          'password': bytes(env['APIAPP_DEFAULTHOMEADMINPASSWORD'] + 'Extra bit to make password wrong','utf-8')
        }, 
          None, #requestedUserID
          connectionContext,
          'a','b','c')
      self.checkGotRightException(context,authFailedException)
    appObj.objectStore.executeInsideTransaction(someFn)

  def test_StandardUserInvalidUsername(self):
    def someFn(connectionContext):    
      masterTenant = GetTenant(masterTenantName, connectionContext, 'a','b','c')
      self.assertEqual(masterTenant.getNumberOfAuthProviders(),1, msg="No internal Auth Providers found")
      singleAuthProvGUID = ""
      for guid in masterTenant.getAuthProviderGUIDList():
        singleAuthProvGUID=guid

      with self.assertRaises(Exception) as context:
        UserIDandRoles = Login(appObj, masterTenantName, singleAuthProvGUID, {
          'username': env['APIAPP_DEFAULTHOMEADMINUSERNAME'] + 'Extra bit to make username wrong',
          'password': get_APIAPP_DEFAULTHOMEADMINPASSWORD_bytes()
        }, 
          None, #requestedUserID
          connectionContext,
          'a','b','c')
      self.checkGotRightException(context,constants.authNotFoundException)
    appObj.objectStore.executeInsideTransaction(someFn)

  def test_StandardUserLoginToInvalidIdentity(self):
    def someFn(connectionContext):    
      masterTenant = GetTenant(masterTenantName, connectionContext, 'a','b','c')
      self.assertEqual(masterTenant.getNumberOfAuthProviders(),1, msg="No internal Auth Providers found")
      singleAuthProvGUID = ""
      for guid in masterTenant.getAuthProviderGUIDList():
        singleAuthProvGUID=guid
        
      with self.assertRaises(Exception) as context:
        UserIDandRoles = Login(
          appObj, 
          masterTenantName, 
          singleAuthProvGUID, 
          {
            'username': env['APIAPP_DEFAULTHOMEADMINUSERNAME'],
            'password': bytes(self.getDefaultHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(masterTenant.getAuthProvider(singleAuthProvGUID)['saltForPasswordHashing']),'utf-8')
          }, 
          'invalid_identity_guid', #requestedUserID
          connectionContext,
          'a','b','c'
        )
      self.checkGotRightException(context,UnknownUserIDException)
      
    appObj.objectStore.executeInsideTransaction(someFn)

  # Person can log in and choose to use userA or userB
  def test_oneAuthCanAccessTwoIdentities(self):
    def someFn(connectionContext):    
      userID1 = 'TestUser1'
      userID2 = 'TestUser2'
      InternalAuthUsername = 'ABC'
      res = self.createTwoUsersForOnePerson(userID1, userID2, InternalAuthUsername, connectionContext)
      
      #Login and get list of identities
      UserIDandRoles = Login(
        appObj, 
        masterTenantName, 
        res['authProvGUID'], 
        {
          'username': InternalAuthUsername,
          'password': get_APIAPP_DEFAULTHOMEADMINPASSWORD_bytes()
        },
        None, #requestedUserID
        connectionContext,
        'a','b','c'
      )
      foundIdentity1 = False
      foundIdentity2 = False
      for curUserID in UserIDandRoles['possibleUserIDs']:
        if userID1 == curUserID:
          foundIdentity1 = True
        if userID2 == curUserID:
          foundIdentity2 = True
      self.assertTrue(foundIdentity1, msg="Identity 1 was not returned when list of login identities to use was given")
      self.assertTrue(foundIdentity2, msg="Identity 2 was not returned when list of login identities to use was given")
      
      #Try and log in using identities
      UserIDandRoles = Login(
        appObj, 
        masterTenantName, 
        res['authProvGUID'], 
        {
          'username': InternalAuthUsername,
          'password': get_APIAPP_DEFAULTHOMEADMINPASSWORD_bytes()
        }, 
        userID1, #requestedUserID
        connectionContext,
        'a','b','c'
      )
      expectedJSONResponse = {
        'TenantRoles': {"usersystem": [DefaultHasAccountRole]}, 
        'UserID': userID1, 
        "exp": "xx", 
        "iss": userID1,
        "authedPersonGuid": res['person']['guid'],
        "known_as": userID1,
        "other_data": {
          "createdBy": "test/createTwoUsersForOnePerson"
        },
        "currentlyUsedAuthKey": InternalAuthUsername + "@internalDataStore_`@\\/'internal"
      }
      self.assertJSONStringsEqualWithIgnoredKeys(self.decodeToken(UserIDandRoles['jwtData']['JWTToken']), expectedJSONResponse, 
        ['exp','associatedPersons', 'currentlyUsedAuthProviderGuid'], msg="Failed to login to identity 1"
      )
      
      UserIDandRoles = Login(
        appObj, masterTenantName, 
        res['authProvGUID'], 
        {
          'username': InternalAuthUsername,
          'password': get_APIAPP_DEFAULTHOMEADMINPASSWORD_bytes()
        }, 
        userID2, #requestedUserID
        connectionContext,
        'a','b','c'
      )
      expectedJSONResponse = {
        'TenantRoles': {"usersystem": [DefaultHasAccountRole]}, 
        'UserID': userID2, 
        "exp": "xx", 
        "iss": userID2,
        "authedPersonGuid": res['person']['guid'],
        "known_as": userID2,
        "other_data": {
          "createdBy": "test/createTwoUsersForOnePerson"
        },
        "currentlyUsedAuthKey": InternalAuthUsername + "@internalDataStore_`@\\/'internal"
      }
      self.assertJSONStringsEqualWithIgnoredKeys(self.decodeToken(UserIDandRoles['jwtData']['JWTToken']), expectedJSONResponse, 
        ['exp','associatedPersons', 'currentlyUsedAuthProviderGuid'], msg="Failed to login to identity 2"
      )
      
    def dbfn(storeConnection):
      storeConnection.executeInsideTransaction(someFn)
    appObj.objectStore.executeInsideConnectionContext(dbfn)

  #UserA can be shared by many People (Who may or may not have many auths)
  def test_oneUserCanBeAccessedByTwoAuths(self):
    def someFn(connectionContext):    
      masterTenant = GetTenant(masterTenantName, connectionContext, 'a','b','c')
      userID = 'TestUser'
      CreateUser(appObj, {"user_unique_identifier": userID, "known_as": userID}, masterTenantName, 'test/CreateMasterTenant', connectionContext)

      authProvGUID = list(masterTenant.getAuthProviderGUIDList())[0] #Just use first configured authProvider
      person1 = CreatePerson(appObj, connectionContext, None, 'a','b','c')
      person2 = CreatePerson(appObj, connectionContext, None, 'a','b','c')
      InternalAuthUsername1 = 'SomeLogin1'
      InternalAuthUsername2 = 'SomeLogin2'
      authData1 = AddAuth(appObj, masterTenantName, authProvGUID, {
        "username": InternalAuthUsername1, 
        "password": get_APIAPP_DEFAULTHOMEADMINPASSWORD_bytes()
      },
      person1['guid'], connectionContext)
      authData2 = AddAuth(appObj, masterTenantName, authProvGUID, {
        "username": InternalAuthUsername2, 
        "password": get_APIAPP_DEFAULTHOMEADMINPASSWORD_bytes()
      },
      person2['guid'], connectionContext)
      associateUserWithPerson(appObj, userID, person1['guid'], connectionContext)
      associateUserWithPerson(appObj, userID, person2['guid'], connectionContext)

      #Try and log in and make sure both people get access to the user
      UserIDandRoles = Login(appObj, masterTenantName, authProvGUID, {
        'username': InternalAuthUsername1,
        'password': get_APIAPP_DEFAULTHOMEADMINPASSWORD_bytes()
      },
      None,
      connectionContext, 'a','b','c')
      expectedJSONResponse = {
        'TenantRoles': {"usersystem": [DefaultHasAccountRole]}, 
        'UserID': userID, 
        "exp": "xx", 
        "iss": userID,
        "authedPersonGuid": person1['guid'],
        "known_as": userID,
        "other_data": {
          "createdBy": "test/CreateMasterTenant"
        },
        "currentlyUsedAuthKey": InternalAuthUsername1 + "@internalDataStore_`@\\/'internal"
      }
      self.assertJSONStringsEqualWithIgnoredKeys(
        self.decodeToken(UserIDandRoles['jwtData']['JWTToken']), 
        expectedJSONResponse, 
        ['exp', 'associatedPersons', 'currentlyUsedAuthProviderGuid'], 
        msg="Failed to login to identity 1"
      )
      
      UserIDandRoles = Login(
        appObj, 
        masterTenantName, 
        authProvGUID, {
          'username': InternalAuthUsername2,
          'password': get_APIAPP_DEFAULTHOMEADMINPASSWORD_bytes()
        },
        None,
        connectionContext, 'a','b','c'
      )
      expectedJSONResponse['authedPersonGuid'] = person2['guid']
      expectedJSONResponse['currentlyUsedAuthKey'] = InternalAuthUsername2 + "@internalDataStore_`@\\/'internal"
      
      self.assertJSONStringsEqualWithIgnoredKeys(
        self.decodeToken(UserIDandRoles['jwtData']['JWTToken']), 
        expectedJSONResponse, ['exp','associatedPersons', 'currentlyUsedAuthProviderGuid'], 
        msg="Failed to login to identity 2"
      )

    def dbfn(storeConnection):
      storeConnection.executeInsideTransaction(someFn)
      
    appObj.objectStore.executeInsideConnectionContext(dbfn)


