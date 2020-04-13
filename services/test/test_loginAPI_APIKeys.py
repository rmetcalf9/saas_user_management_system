from test_loginAPI import test_api as parent_test_api
import TestHelperSuperClass
import constants
import json

exampleExternalData = {
  "externalKey": {
    "otherData": {
      "A": "a",
      "B": "b",
      "C": "c",
    }
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
          restrictedRoles=None,
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
    self.assertEqual(result.status_code, 201)
    resJSON = json.loads(result.get_data(as_text=True))
    self.assertEqual(resJSON["userID"],userID)
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

#APIKey can be restricted to a single role (Login and check jwt token)

#Deleted API key can not be used

#Test Create API key not possible without valid user id
