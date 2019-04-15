from TestHelperSuperClass import testHelperAPIClientUsingKongStaticGateway, kongISS

from jwtTokenGeneration import generateJWTToken, decodeJWTToken
from appObj import appObj

class test_kongGateway(testHelperAPIClientUsingKongStaticGateway):
  def test_genericTests(self):
    
    userDict = {
      'UserID': 'abc'
    }

    personGUID = "FAKE"
    res = generateJWTToken(appObj, userDict, appObj.APIAPP_JWTSECRET, userDict['UserID'], personGUID)
    generatedJWTToken = res['JWTToken']
    
    jwtSecret = appObj.APIAPP_JWTSECRET
    decodedToken = decodeJWTToken(generatedJWTToken, jwtSecret, True)

    print("decodedToken:",decodedToken)
    
    expectedDecodedToken = {
      'UserID': 'abc', 
      'authedPersonGuid': 'FAKE', 
      'iss': 'abc',
      'kong_iss': kongISS
    }
    
    self.assertJSONStringsEqualWithIgnoredKeys(decodedToken, expectedDecodedToken, [ 'exp' ], msg='Returned JWT Token is wrong')    

