from TestHelperSuperClass import testHelperAPIClientUsingKongStaticGateway, kongISS
from baseapp_for_restapi_backend_with_swagger import decodeJWTToken

from jwtTokenGeneration import generateJWTToken
from appObj import appObj

from MockTenantObj import MockTenantObj


class test_kongGateway(testHelperAPIClientUsingKongStaticGateway):
  def test_genericTests(self):
    
    userDict = {
      'UserID': 'abc'
    }

    personGUID = "FAKE"
    res = generateJWTToken(
      appObj,
      userDict,
      appObj.APIAPP_JWTSECRET,
      userDict['UserID'],
      personGUID,
      'DUMMYcurrentlyUsedAuthProviderGuid',
      'DummyUserAuthKey',
      MockTenantObj(appObj)
    )
    generatedJWTToken = res['JWTToken']
    
    jwtSecret = appObj.APIAPP_JWTSECRET
    
    decodedToken = decodeJWTToken(generatedJWTToken, jwtSecret, True)

    ##print("decodedToken:",decodedToken)
    
    expectedDecodedToken = {
      'UserID': 'abc', 
      'authedPersonGuid': 'FAKE', 
      'iss': 'abc',
      'kong_iss': kongISS,
      'currentlyUsedAuthProviderGuid': 'DUMMYcurrentlyUsedAuthProviderGuid',
      "currentlyUsedAuthKey": "DummyUserAuthKey"
    }
    
    self.assertJSONStringsEqualWithIgnoredKeys(decodedToken, expectedDecodedToken, [ 'exp' ], msg='Returned JWT Token is wrong')    

