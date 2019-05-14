from TestHelperSuperClass import testHelperAPIClient, env, getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse
import constants
import json
import copy
from tenants import CreatePerson, GetTenant, _getAuthProvider
from appObj import appObj
from authProviders import authProviderFactory
from authProviders_base import getAuthRecord
import urllib

class currentAuthLinkSetups(testHelperAPIClient):
  def linkInternalUserToLoggedInUser(self, tenant, loginDictForUserToLinkTo, authProviderDICT, username, password, expectedResults = [200]):
    hashedPassword = getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(
      username, 
      password, 
      authProviderDICT['saltForPasswordHashing']
    )
    
    linkJSON = {
      "authProviderGUID": authProviderDICT['guid'],
      "credentialJSON": { 
        "username": username, 
        "password": hashedPassword
       }
    }
    result2 = self.testClient.post(
      self.currentAuthAPIPrefix + '/' + tenant + '/loggedInUserAuths/link', 
      data=json.dumps(linkJSON), 
      content_type='application/json',
      headers={ constants.jwtHeaderName: loginDictForUserToLinkTo['jwtData']['JWTToken']}
    )
    for x in expectedResults:
      if result2.status_code == x:
        return json.loads(result2.get_data(as_text=True))
    print(result2.get_data(as_text=True))
    self.assertFalse(True, msg="Login status_code was " + str(result2.status_code) + " expected one of " + str(expectedResults))
    return None

  
class test_currentAuthLinkTests(currentAuthLinkSetups):
  
  def test_callAPIWithNoUserFails(self):
    linkJSON = {
      "authProviderGUID": 'asd',
      "credentialJSON": { 
        "username": 'aaa', 
        "password": 'bb'
       }
    }
    result2 = self.testClient.post(
      self.currentAuthAPIPrefix + '/' + constants.masterTenantName + '/loggedInUserAuths/link', 
      data=json.dumps(linkJSON), 
      content_type='application/json'
    )
    self.assertEqual(result2.status_code, 401, msg="Was able to call API without logged in credentials")
    result2JSON = json.loads(result2.get_data(as_text=True))
    self.assertEqual(result2JSON['message'],"No JWT Token in header or cookie")

  # This test will be changed at a later date as we add person de-dup functionality
  def test_linkWithExistingAuthReturnsError(self):
    defaultUserLoginDict = self.loginAsDefaultUser()
    masterTenantDict = self.getTenantDICT(constants.masterTenantName)
    masterTenantDict['AuthProviders'][0]["AllowUserCreation"] = True
    masterTenantDict["AllowUserCreation"] = True
    masterTenantDict = self.updateTenant(masterTenantDict, [200])

    username = "testSetUserName"
    password = "delkjgn4rflkjwned"
    
    createdAuthProvGUID = masterTenantDict['AuthProviders'][0]['guid']
    createdAuthSalt = masterTenantDict['AuthProviders'][0]['saltForPasswordHashing']
    
    registerResultJSON = self.registerInternalUser(masterTenantDict['Name'], username, password, masterTenantDict['AuthProviders'][0])
    
    #make sure login as newly registered user works
    self.loginAsUser(
      masterTenantDict['Name'], 
      masterTenantDict['AuthProviders'][0], 
      username, 
      password, 
      [200]
    )

    # Now try and link default user with newly created users autuh
    linkUserResponseDict = self.linkInternalUserToLoggedInUser(
      constants.masterTenantName, 
      defaultUserLoginDict, 
      masterTenantDict['AuthProviders'][0], 
      username, 
      password, 
      [400]
    )
    self.assertEqual(linkUserResponseDict['message'], 'personOBj._linkExistantAuth Not Implemented', msg="Link User Response wrong")


