from test_loginAPI import test_api as parent_test_api
import TestHelperSuperClass
import constants
import json

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

class helper(parent_test_api):
  def setup(self):
    # Setup Create 3 users and each user has 3 APIKeys

    userInfos = []
    userInfos.append({
      "name": "testUser001",
      "pass": "p001",
      "userDict": {
        "UserID": "testUser001",
        "TenantRoles": { constants.masterTenantName: [ constants.DefaultHasAccountRole ]}
      }
    })
    userInfos.append({
      "name": "testUser002",
      "pass": "p002",
      "userDict": {
        "UserID": "testUser001",
        "TenantRoles": { constants.masterTenantName: [ constants.DefaultHasAccountRole ]}
      }
    })
    userInfos.append({
      "name": "testUser003",
      "pass": "p003",
      "userDict": {
        "UserID": "testUser001",
        "TenantRoles": { constants.masterTenantName: [ constants.DefaultHasAccountRole ]}
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
    externalData
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
    self.assertEqual(result.status_code, 201, msg="Unexpected return - " + result.get_data(as_text=True))
    resJSON = json.loads(result.get_data(as_text=True))
    self.assertEqual(resJSON["apikeydata"]["tenantName"],tenant)
    self.assertEqual(resJSON["apikeydata"]["createdByUserID"],userID)
    self.assertEqual(resJSON["apikeydata"]["restrictedRoles"],restrictedRoles)
    self.assertEqual(resJSON["apikeydata"]["externalData"],externalData)
    self.assertNotEqual(resJSON["apikeydata"]["id"],resJSON["apikey"], msg="APIKey must not be same as the id of the data (should be hashed with userid and instance password")
    return resJSON

@TestHelperSuperClass.wipd
class test_loginAPI_APIKEys(helper):
  def test_CreateAPIKeyandQueryBack(self):
    # Create APIKey and query back works
    # Query back API key dosen't contain apikey
    setupData = self.setup()

    print("setupData", setupData)

    raise Exception("Not Implemented")


#create api key on invalid tenant fails

#User can not query back another users api keys

#Login with API key works

#User can not use API key on wrong tenant

#APIKey can be restricted to a single role (Login and check jwt token)

#Deleted API key can not be used

#Test Create API key not possible without valid user id
