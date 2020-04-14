from test_loginAPI import test_api as parent_test_api
import TestHelperSuperClass
import constants
import json
import uuid
from appObj import appObj
import python_Testing_Utilities
import object_store_abstraction

exampleExternalData = {
  "externalKey": "someKeyXXX",
  "otherData": {
    "A": "a",
    "B": "b",
    "C": "c"
  }
}

sampleCreateAPIKeyRequest = {
  "restrictedToRoles": [],
  "externalData": exampleExternalData
}

secondTenantName="secondTenant"
extraRoleGrantedToUser="ExtraRoleUserGranted"
userTenantRoles = {
  constants.masterTenantName: [ constants.DefaultHasAccountRole, extraRoleGrantedToUser, "ExtraRoleBUserNotGranted" ],
  secondTenantName: [ constants.DefaultHasAccountRole ]
}

class helper(parent_test_api):
  def setup(self):
    # Setup Create 3 users and each user has 3 APIKeys

    userInfos = []
    userInfos.append({
      "name": "testUser001",
      "pass": "p001",
      "userDict": {
        "UserID": "testUser001",
        "TenantRoles": userTenantRoles
      }
    })
    userInfos.append({
      "name": "testUser002",
      "pass": "p002",
      "userDict": {
        "UserID": "testUser002",
        "TenantRoles": userTenantRoles
      }
    })
    userInfos.append({
      "name": "testUser003",
      "pass": "p003",
      "userDict": {
        "UserID": "testUser003",
        "TenantRoles": userTenantRoles
      }
    })

    userPassBack = []
    for useInfo in userInfos:
      self.createIntarnalLoginForTenant(
        tenantName=constants.masterTenantName,
        userID=useInfo["name"],
        InternalAuthUsername=useInfo["name"],
        InternalAuthPassword=useInfo["pass"]
      )
      self.AddRoleToUser(
        userID=useInfo["userDict"]["UserID"],
        tenantName=constants.masterTenantName,
        rolesToAdd=[ extraRoleGrantedToUser ]
      )

      userAuthToken = self.generateJWTToken(useInfo["userDict"])

      APIKeyCreationResults = []
      for x in range(1, 4): #1,2,3
        resValue = self.CreateAPIKey(
          tenant=constants.masterTenantName,
          userID=useInfo["name"],
          userAuthToken=userAuthToken,
          restrictedRoles=[],
          externalData=exampleExternalData
        )

        APIKeyCreationResults.append({
          "res": resValue
        })

      userPassBack.append({
        "userName": useInfo["name"],
        "userID": useInfo["userDict"]["UserID"],
        "userAuthToken": userAuthToken,
        "APIKeyCreationResults": APIKeyCreationResults
      })

    return {
      "users": userPassBack
    }

  def CreateAPIKey(
    self,
    tenant,
    userID,
    userAuthToken,
    restrictedRoles,
    externalData,
    checkAndParseResponse=True
  ):
    if restrictedRoles is None:
      raise Exception("restrictedRoles can't be none - pass an empty list for no restriction")
    postJSON = {
      "restrictedRoles": restrictedRoles,
      "externalData": externalData
    }
    result = self.testClient.post(
      self.loginAPIPrefix + '/' + tenant + '/apikeys',
      headers={ constants.jwtHeaderName: userAuthToken},
      data=json.dumps(postJSON),
      content_type='application/json'
    )
    if not checkAndParseResponse:
      return result
    self.assertEqual(result.status_code, 201, msg="Unexpected return - " + result.get_data(as_text=True))
    resJSON = json.loads(result.get_data(as_text=True))
    self.assertEqual(resJSON["apikeydata"]["tenantName"],tenant)
    self.assertEqual(resJSON["apikeydata"]["createdByUserID"],userID)
    self.assertEqual(resJSON["apikeydata"]["restrictedRoles"],restrictedRoles)
    self.assertEqual(resJSON["apikeydata"]["externalData"],externalData)
    self.assertNotEqual(resJSON["apikeydata"]["id"],resJSON["apikey"], msg="APIKey must not be same as the id of the data (should be hashed with userid and instance password")
    return resJSON

  def getAPIKey(
    self,
    tenant,
    userAuthToken,
    apiKeyID,
    checkAndParseResponse=True
  ):
    result = self.testClient.get(
      self.loginAPIPrefix + '/' + tenant + '/apikeys/' + apiKeyID,
      headers={ constants.jwtHeaderName: userAuthToken},
      data=None,
      content_type='application/json'
    )
    if not checkAndParseResponse:
      return result
    self.assertEqual(result.status_code, 200, msg="Unexpected return - " + result.get_data(as_text=True))
    resJSON = json.loads(result.get_data(as_text=True))
    return resJSON

  def getAPIKeysForUser(
    self,
    tenant,
    userAuthToken,
    checkAndParseResponse=True
  ):
    result = self.testClient.get(
      self.loginAPIPrefix + '/' + tenant + '/apikeys',
      headers={ constants.jwtHeaderName: userAuthToken},
      data=None,
      content_type='application/json'
    )
    if not checkAndParseResponse:
      return result
    self.assertEqual(result.status_code, 200, msg="Unexpected return - " + result.get_data(as_text=True))
    resJSON = json.loads(result.get_data(as_text=True))
    return resJSON

  def deleteAPIKey(self, tenant, userAuthToken, apiKeyID, objectVersionNumber, checkAndParseResponse=True):
    result = self.testClient.delete(
      self.loginAPIPrefix + '/' + tenant + '/apikeys/' + apiKeyID + "?objectversion=" + objectVersionNumber,
      headers={ constants.jwtHeaderName: userAuthToken},
      data=None,
      content_type='application/json'
    )
    if not checkAndParseResponse:
      return result
    self.assertEqual(result.status_code, 202)
    return json.loads(result.get_data(as_text=True))

  def loginUsingAPIToken(self, tenant, apiKey, checkAndParseResponse=True):
    result = self.testClient.get(
      self.loginAPIPrefix + '/' + tenant + '/apikeylogin',
      headers={ "Authorization": "Bearer " + apiKey},
      data=None,
      content_type='application/json'
    )
    if not checkAndParseResponse:
      return result
    self.assertEqual(result.status_code, 200, msg="Unexpected return - " + result.get_data(as_text=True))
    resDICT = json.loads(result.get_data(as_text=True))
    return resDICT

@TestHelperSuperClass.wipd
class test_loginAPI_APIKeys(helper):
  def test_CreateAPIKeyandQueryBack(self):
    # Create APIKey and query back works
    # Query back API key dosen't contain apikey
    setupData = self.setup()

    user = setupData["users"][0]
    apiKeyDataToUse = user["APIKeyCreationResults"][0]["res"]["apikeydata"]

    retrievedAPIKeyJSON = self.getAPIKey(
      tenant=apiKeyDataToUse["tenantName"],
      userAuthToken=user["userAuthToken"],
      apiKeyID=apiKeyDataToUse["id"]
    )

    python_Testing_Utilities.assertObjectsEqual(
      unittestTestCaseClass=self,
      first=retrievedAPIKeyJSON,
      second=user["APIKeyCreationResults"][0]["res"]["apikeydata"],
      msg="Didn't get expected result",
      ignoredRootKeys=[]
    )

  def test_createApiKeyOnInvalidTenantFails(self):
    setupData = self.setup()
    user = setupData["users"][0]

    result = self.CreateAPIKey(
      tenant=secondTenantName + "INV",
      userID=user["userID"],
      userAuthToken=user["userAuthToken"],
      restrictedRoles=[],
      externalData={},
      checkAndParseResponse=False
    )
    self.assertEqual(result.status_code, 403, msg="Unexpected return - " + result.get_data(as_text=True))
    resultDict = json.loads(result.get_data(as_text=True))
    self.assertEqual(resultDict["message"],"Missing required Role")

  def test_queryValidAPIKeyOnWrongTenantFails(self):
    setupData = self.setup()
    user = setupData["users"][0]
    apiKeyDataToUse = user["APIKeyCreationResults"][0]["res"]["apikeydata"]

    result = self.getAPIKey(
      tenant=secondTenantName,
      userAuthToken=user["userAuthToken"],
      apiKeyID=apiKeyDataToUse["id"],
      checkAndParseResponse=False
    )
    self.assertEqual(result.status_code, 404, msg="Unexpected return - " + result.get_data(as_text=True))
    resultDict = json.loads(result.get_data(as_text=True))
    self.assertEqual(resultDict["message"],"The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.")


  def test_UserCanNotQueryBackAnotherUsersKey(self):
    setupData = self.setup()

    user = setupData["users"][0]
    userDoingQuery = setupData["users"][1]
    apiKeyDataToUse = user["APIKeyCreationResults"][0]["res"]["apikeydata"]

    result = self.getAPIKey(
      tenant=apiKeyDataToUse["tenantName"],
      userAuthToken=userDoingQuery["userAuthToken"],
      apiKeyID=apiKeyDataToUse["id"],
      checkAndParseResponse=False
    )
    self.assertEqual(result.status_code, 404, msg="Unexpected return - " + result.get_data(as_text=True))
    resultDict = json.loads(result.get_data(as_text=True))
    self.assertEqual(resultDict["message"],"The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.")

    ##Repeat test using paginated result query making sure this key is not present
    resultDict = self.getAPIKeysForUser(
      tenant=apiKeyDataToUse["tenantName"],
      userAuthToken=userDoingQuery["userAuthToken"],
      checkAndParseResponse=True
    )
    self.assertEqual(resultDict["pagination"]["total"], 3) # there should be 3 results for this user
    self.assertEqual(len(resultDict["result"]), 3) # there should be 3 results for this user

    for result in resultDict["result"]:
      self.assertNotEqual(result["id"], apiKeyDataToUse["id"])

  #************************************************************************
  #************************ login tests below *****************************
  #************************************************************************

  def test_loginWithNoHeaderFails(self):
    result = self.testClient.get(
      self.loginAPIPrefix + '/' + constants.masterTenantName + '/apikeylogin',
      headers=None,
      data=None,
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg="Unexpected return - " + result.get_data(as_text=True))
    resultDict = json.loads(result.get_data(as_text=True))
    self.assertEqual(resultDict["message"],"Missing Authorization Header")

  def test_loginWithBadAuthHeaderFails(self):
    result = self.testClient.get(
      self.loginAPIPrefix + '/' + constants.masterTenantName + '/apikeylogin',
      headers={ "Authorization": "BadValue " + "ss" },
      data=None,
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg="Unexpected return - " + result.get_data(as_text=True))
    resultDict = json.loads(result.get_data(as_text=True))
    self.assertEqual(resultDict["message"],"Invalid Authorization Header")

  def test_loginWithInvliadAPIKeyFails(self):
    apiKey = "InvalidAPIKey"
    result = self.testClient.get(
      self.loginAPIPrefix + '/' + constants.masterTenantName + '/apikeylogin',
      headers={"Authorization": "Bearer " + apiKey},
      data=None,
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg="Unexpected return - " + result.get_data(as_text=True))
    resultDict = json.loads(result.get_data(as_text=True))
    self.assertEqual(resultDict["message"], "Invalid API Key")

  def test_UserCanNotUseAPIKeyOnWrongTenant(self):
    setupData = self.setup()
    user = setupData["users"][0]
    apiKey = user["APIKeyCreationResults"][0]["res"]["apikey"]

    result = self.loginUsingAPIToken(
      tenant=secondTenantName,
      apiKey=apiKey,
      checkAndParseResponse=False
    )
    self.assertEqual(result.status_code, 400, msg="Unexpected return - " + result.get_data(as_text=True))
    resultDict = json.loads(result.get_data(as_text=True))
    self.assertEqual(resultDict["message"], "Invalid API Key")

  def test_loginUsingAPIToken(self):
    setupData = self.setup()

    user = setupData["users"][0]
    apiKey = user["APIKeyCreationResults"][0]["res"]["apikey"]

    JWTTokenResponse = self.loginUsingAPIToken(
      tenant=constants.masterTenantName,
      apiKey=apiKey
    )

    self.assertEqual(JWTTokenResponse["possibleUsers"],None)
    self.assertEqual(JWTTokenResponse["known_as"],user["userID"])

    jwtTokenDict = self.decodeToken(JWTTokenResponse[ 'jwtData' ]['JWTToken'])
    self.assertEqual(jwtTokenDict["UserID"],user["userID"])
    self.assertEqual(jwtTokenDict["TenantRoles"],{ constants.masterTenantName: [ constants.DefaultHasAccountRole, extraRoleGrantedToUser ] })

  def test_loginWithUserWithNoHasACcountRoleFails(self):
    setupData = self.setup()

    user = setupData["users"][0]
    apiKey = user["APIKeyCreationResults"][0]["res"]["apikey"]

    # First login should be sucessful
    JWTTokenResponse = self.loginUsingAPIToken(
      tenant=constants.masterTenantName,
      apiKey=apiKey
    )

    #Remove has account role for user
    self.RemoveRoleFromUser(
      userID=user["userID"],
      tenantName=constants.masterTenantName,
      rolesToRemove=[ constants.DefaultHasAccountRole ]
    )

    result = self.loginUsingAPIToken(
      tenant=constants.masterTenantName,
      apiKey=apiKey,
      checkAndParseResponse=False
    )
    self.assertEqual(result.status_code, 400, msg="Unexpected return - " + result.get_data(as_text=True))
    resultDict = json.loads(result.get_data(as_text=True))
    self.assertEqual(resultDict["message"], "Invalid API Key")

  def test_apikey_with_restricted_roles(self):
    # Note: Has account role is not restricted and is always present
    # users with no hasaccount role have all their apitokens disabled
    userWithManyRoles = {
      "name": "testUserWithManyRoles",
      "pass": "p001",
      "userDict": {
        "UserID": "testUserWithManyRoles",
        "TenantRoles": userTenantRoles
      }
    }
    self.createIntarnalLoginForTenant(
      tenantName=constants.masterTenantName,
      userID=userWithManyRoles["name"],
      InternalAuthUsername=userWithManyRoles["name"],
      InternalAuthPassword=userWithManyRoles["pass"]
    )
    self.AddRoleToUser(
      userID=userWithManyRoles["userDict"]["UserID"],
      tenantName=constants.masterTenantName,
      rolesToAdd=[ "role001", "role002", "role003", "role004", "role005", "role006", "role007", "role008", "role009" ]
    )

    userAuthToken = self.generateJWTToken(userWithManyRoles["userDict"])

    apiKeyWithRestrictedRoles = self.CreateAPIKey(
      tenant=constants.masterTenantName,
      userID=userWithManyRoles["name"],
      userAuthToken=userAuthToken,
      restrictedRoles=[ "role001", "role002", "role003" ],
      externalData=exampleExternalData
    )

    JWTTokenResponse = self.loginUsingAPIToken(
      tenant=constants.masterTenantName,
      apiKey=apiKeyWithRestrictedRoles["apikey"]
    )

    self.assertEqual(JWTTokenResponse["possibleUsers"],None)
    self.assertEqual(JWTTokenResponse["known_as"],userWithManyRoles["userDict"]["UserID"])

    jwtTokenDict = self.decodeToken(JWTTokenResponse[ 'jwtData' ]['JWTToken'])
    print("jwtTokenDict:", jwtTokenDict)
    self.assertEqual(jwtTokenDict["UserID"],userWithManyRoles["userDict"]["UserID"])
    self.assertEqual(jwtTokenDict["TenantRoles"][constants.masterTenantName],[ constants.DefaultHasAccountRole, "role001", "role002", "role003" ])


  def test_loginUsingDeletedAPIKeyFails(self):
    setupData = self.setup()

    user = setupData["users"][0]
    apiKeyDataToUse = user["APIKeyCreationResults"][0]["res"]["apikeydata"]
    apiKey = user["APIKeyCreationResults"][0]["res"]["apikey"]

    JWTTokenResponse = self.loginUsingAPIToken(
      tenant=constants.masterTenantName,
      apiKey=apiKey
    )

    retrievedAPIKeyJSON = self.getAPIKey(
      tenant=apiKeyDataToUse["tenantName"],
      userAuthToken=user["userAuthToken"],
      apiKeyID=apiKeyDataToUse["id"]
    )

    objectVersionNumber = retrievedAPIKeyJSON[object_store_abstraction.RepositoryObjBaseClass.getMetadataElementKey()]["objectVersion"]

    #Delete APIKey
    self.deleteAPIKey(
      tenant=apiKeyDataToUse["tenantName"],
      userAuthToken = user["userAuthToken"],
      apiKeyID=apiKeyDataToUse["id"],
      objectVersionNumber=objectVersionNumber
    )

    result = self.loginUsingAPIToken(
      tenant=constants.masterTenantName,
      apiKey=apiKey,
      checkAndParseResponse=False
    )
    self.assertEqual(result.status_code, 400, msg="Unexpected return - " + result.get_data(as_text=True))
    resultDict = json.loads(result.get_data(as_text=True))
    self.assertEqual(resultDict["message"], "Invalid API Key")

  def testHashFunction(self):
    #Make sure I get different reuslts with different API keys
    APIKeys = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
    Hashed = []
    for APIKey in APIKeys:
      Hashed.append(appObj.ApiKeyManager.getHashedAPIKey(APIKey=APIKey))

    for cur in [0,1,2]:
      for cur2 in [0,1,2]:
        if cur != cur2:
          self.assertNotEqual(Hashed[cur], Hashed[cur2], msg="Got two identical hashes")

