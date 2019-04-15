from datetime import timedelta
from expiringdict import expiringdictClass
import secrets
import copy
from jwtTokenGeneration import generateJWTToken

def generateRandomRefreshToken(appObj):
  return secrets.token_urlsafe()

# Class to hold all the refresh data in memory
class RefreshTokenManager():
  refreshTokenDict = None
  
  def __init__(self, appObj):
    self.refreshTokenDict = expiringdictClass(appObj.APIAPP_REFRESH_TOKEN_TIMEOUT, appObj.scheduler, appObj.getCurDateTime)

  
    
  def generateRefreshTokenFirstTime(self, appObj, userAuthInformationWithoutJWTorRefreshToken, userDict, key, personGUID):
    token = generateRandomRefreshToken(appObj)
    dataToStoreWithRefreshToken = {
      'userAuthInformationWithoutJWTorRefreshToken': copy.deepcopy(userAuthInformationWithoutJWTorRefreshToken),
      'userDict': userDict, 
      'key': key, 
      'personGUID': personGUID,
      'refreshSessionExpiry': appObj.getCurDateTime() + timedelta(seconds=int(appObj.APIAPP_REFRESH_SESSION_TIMEOUT))
    }
    self.refreshTokenDict.addOrReplaceKey(appObj.getCurDateTime(), token, dataToStoreWithRefreshToken)
  
    expiryTime = appObj.getCurDateTime() + timedelta(seconds=int(appObj.APIAPP_REFRESH_TOKEN_TIMEOUT))

    return {
      'token': token,
      'TokenExpiry': expiryTime
    }

  def getRefreshedAuthDetails(self, appObj, existingToken):
    try:
      val = self.refreshTokenDict.popValue(appObj.getCurDateTime(), existingToken)
    except KeyError:
      return None
    
    if val['refreshSessionExpiry'] < appObj.getCurDateTime():
      return None
    
    token = generateRandomRefreshToken(appObj)
    self.refreshTokenDict.addOrReplaceKey(appObj.getCurDateTime(), token, val)
    expiryTime = appObj.getCurDateTime() + timedelta(seconds=int(appObj.APIAPP_REFRESH_TOKEN_TIMEOUT))
    
    
    userAuthInfo = copy.deepcopy(val['userAuthInformationWithoutJWTorRefreshToken'])
    userAuthInfo['jwtData'] = generateJWTToken(
      appObj, 
      val['userDict'], 
      appObj.APIAPP_JWTSECRET, 
      val['key'], 
      val['personGUID']
    )
    userAuthInfo['refresh'] = {
      'token': token,
      'TokenExpiry': expiryTime
    }
    
    return userAuthInfo
  
  
