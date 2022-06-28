from TestHelperSuperClass import testHelperAPIClient, env, getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse
from constants import masterTenantName, jwtHeaderName, jwtCookieName, DefaultHasAccountRole, masterTenantDefaultSystemAdminRole, objectVersionHeaderName
import json
import copy
from tenants import CreatePerson, GetTenant, _getAuthProvider
from appObj import appObj
from AuthProviders import authProviderFactory
from AuthProviders.authProviders_base import getAuthRecord
import urllib

class currentAuthUnlinkSetups(testHelperAPIClient):
  def deleteAuthKey(self, authKey, loginDICT, expectedResults):
    postData = {"AuthKey": authKey}
    deleteResult = self.testClient.post(
      self.currentAuthAPIPrefix + '/' + masterTenantName + '/loggedInUserAuths/delete',
      headers={ jwtHeaderName: loginDICT['jwtData']['JWTToken']}, 
      data=json.dumps(postData), 
      content_type='application/json'
    )
    for x in expectedResults:
      if x == deleteResult.status_code:
        return json.loads(deleteResult.get_data(as_text=True))
    self.assertTrue(False, msg="Delete Auth gave wrong response - " + deleteResult.get_data(as_text=True)) 

class test_currentAuthUnlinkTests(currentAuthUnlinkSetups):
  def test_deleteNonExistantAuthFails(self):
    loginDICT = self.loginAsDefaultUser()
    authKey = 'aabbcc'
    deleteDICT = self.deleteAuthKey(authKey, loginDICT, [400])
    self.assertJSONStringsEqualWithIgnoredKeys(
      deleteDICT, 
      {"message": "Auth with this key dosen't exist"}, 
      [], 
      msg='JSON of created Tenant is not the same'
    )
    
  # Can't delete auth the the user currently used to login
  def test_deleteAuthUsedToLoginWithFails(self):
    loginDICT = self.loginAsDefaultUser()
    authKey = loginDICT['currentlyUsedAuthKey']
    deleteDICT = self.deleteAuthKey(authKey, loginDICT, [400])
    self.assertJSONStringsEqualWithIgnoredKeys(
      deleteDICT, 
      {"message": "Can't unlinked auth used to authenticate"}, 
      [], 
      msg='Error message wrong'
    )
    
  # Can't delete auth that is not for logged in user
  def test_deleteAuthForDifferentUserFails(self):
    masterTenantDict = self.getTenantDICT(masterTenantName)
    masterTenantDict["AllowUserCreation"] = True
    masterTenantDict['AuthProviders'][0]["AllowUserCreation"] = True
    masterTenantDict = self.updateTenant(masterTenantDict, [200])
    
    userName = "testSetUserName"
    password = "delkjgn4rflkjwned"
    
    createdAuthProvGUID = masterTenantDict['AuthProviders'][0]['guid']
    createdAuthSalt = masterTenantDict['AuthProviders'][0]['saltForPasswordHashing']
    
    registerResultJSON = self.registerInternalUser(
      masterTenantDict['Name'], 
      userName, 
      password, 
      masterTenantDict['AuthProviders'][0]
    )
    
    newlyRegisteredUserLoginDict = self.loginAsUser(masterTenantDict['Name'], masterTenantDict['AuthProviders'][0], userName, password, [200])
    
    newlyRegisteredUsersAuthKey = newlyRegisteredUserLoginDict['currentlyUsedAuthKey']

    #We have setup a user and retrieved their auth key
    ## now we login as another user and try and delete their auth key
    ## this should fail
    loginDICT = self.loginAsDefaultUser()

    
    deleteDICT = self.deleteAuthKey(newlyRegisteredUsersAuthKey, loginDICT, [400])
    self.assertJSONStringsEqualWithIgnoredKeys(
      deleteDICT, 
      {"message": "Can only unlink own auths"}, 
      [], 
      msg='Error message wrong'
    )


  # Can't delete auth for auth provider that does not allow unlink
  def test_deleteAuthProviderThatDosNotAllowUnlinkFails(self):
    masterTenantDict = self.getTenantDICT(masterTenantName)
    masterTenantDict['AuthProviders'][0]["AllowUnlink"] = False
    masterTenantDict = self.updateTenant(masterTenantDict, [200])

    loginDICT = self.loginAsDefaultUser()

    
    #create an auth to delete
    newAuthDICT = self.getNewAuthDICT()
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths', 
      headers={ jwtHeaderName: loginDICT['jwtData']['JWTToken']}, 
      data=json.dumps(newAuthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 201, msg="Create auth failed - " + result.get_data(as_text=True))
    newAuthDICT = json.loads(result.get_data(as_text=True))
    
    deleteDICT = self.deleteAuthKey(newAuthDICT['AuthUserKey'], loginDICT, [400])
    self.assertJSONStringsEqualWithIgnoredKeys(
      deleteDICT, 
      {"message": "Auth provider dosn't allow unlinking"}, 
      [], 
      msg='Error message wrong'
    )
    
  # Can't delete users last auth - test not needed since we have a test
  # that ensures we can't delete the logged in auth so it would always
  # be impossible to delete the last auth

  # Sucessful unlink of auth
  def test_deleteAuthProviderThatDosNotAllowUnlinkFails(self):
    masterTenantDict = self.getTenantDICT(masterTenantName)
    masterTenantDict['AuthProviders'][0]["AllowUnlink"] = True
    masterTenantDict = self.updateTenant(masterTenantDict, [200])

    loginDICT = self.loginAsDefaultUser()
    
    #create an auth to delete
    newAuthUsername = "newAuthUserNAmeDDD"
    newAuthDICT = self.getNewAuthDICT(newAuthUsername)
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/auths', 
      headers={ jwtHeaderName: loginDICT['jwtData']['JWTToken']}, 
      data=json.dumps(newAuthDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 201, msg="Create auth failed - " + result.get_data(as_text=True))
    newAuthDICTRec = json.loads(result.get_data(as_text=True))
    
    #Login with the auth to delete and make sure it works
    self.loginAsUser(
      masterTenantDict['Name'], 
      masterTenantDict['AuthProviders'][0], 
      newAuthUsername, 
      env['APIAPP_DEFAULTHOMEADMINPASSWORD'], 
      [200]
    )
    
    deleteDICT = self.deleteAuthKey(newAuthDICTRec['AuthUserKey'], loginDICT, [200])

    #Login with the auth to delete and make sure it fails (because the auth should be deleted)
    self.loginAsUser(
      masterTenantDict['Name'], 
      masterTenantDict['AuthProviders'][0], 
      newAuthUsername, 
      env['APIAPP_DEFAULTHOMEADMINPASSWORD'], 
      [401]
    )
    
    #Query current user info to make sure it still works - with existing login:
    result = self.testClient.get(
      self.currentAuthAPIPrefix + '/' + masterTenantName + '/currentAuthInfo', 
      headers={ jwtHeaderName: loginDICT['jwtData']['JWTToken']}
    )
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))
    
    #Query current user info to make sure it still works - with NEW login:
    NEWloginDICT = self.loginAsDefaultUser()
    result = self.testClient.get(
      self.currentAuthAPIPrefix + '/' + masterTenantName + '/currentAuthInfo', 
      headers={ jwtHeaderName: NEWloginDICT['jwtData']['JWTToken']}
    )
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))
    
    

