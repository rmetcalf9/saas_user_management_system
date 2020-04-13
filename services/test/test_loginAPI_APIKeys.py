from test_loginAPI import test_api as parent_test_api
import TestHelperSuperClass
import constants
import json
import uuid
from appObj import appObj
import python_Testing_Utilities

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
userTenantRoles = {
  constants.masterTenantName: [ constants.DefaultHasAccountRole ],
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


#Login with API key works

#User can not use API key on wrong tenant

#APIKey can be restricted to a single role (Login and check jwt token)

#Deleted API key can not be used

#Test Create API key not possible without valid user id



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

