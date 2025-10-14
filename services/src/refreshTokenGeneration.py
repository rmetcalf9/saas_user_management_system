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

  def generateRefreshTokenFirstTime(
    self,
    appObj,
    userAuthInformationWithoutJWTorRefreshToken,
    userDict,
    key,
    personGUID,
    currentlyUsedAuthProviderGuid,
    currentlyUsedAuthKey,
    tenantObj
  ):
    token = generateRandomRefreshToken(appObj)
    dataToStoreWithRefreshToken = {
      'userAuthInformationWithoutJWTorRefreshToken': copy.deepcopy(userAuthInformationWithoutJWTorRefreshToken),
      'userDict': userDict,
      'key': key,
      'personGUID': personGUID,
      'currentlyUsedAuthProviderGuid': currentlyUsedAuthProviderGuid,
      'currentlyUsedAuthKey': currentlyUsedAuthKey,
      'refreshSessionExpiry': appObj.getCurDateTime() + timedelta(seconds=int(appObj.APIAPP_REFRESH_SESSION_TIMEOUT))
    }
    self.refreshTokenDict.addOrReplaceKey(appObj.getCurDateTime(), token, dataToStoreWithRefreshToken)

    print("DEBUG appObj.APIAPP_REFRESH_TOKEN_TIMEOUT", appObj.APIAPP_REFRESH_TOKEN_TIMEOUT)
    print("DEBUG tenantObj.getRefreshTokenTimeout()", tenantObj.getRefreshTokenTimeout())
    expiryTime = appObj.getCurDateTime() + timedelta(seconds=int(tenantObj.getRefreshTokenTimeout()))

    return {
      'token': token,
      'TokenExpiry': expiryTime.isoformat()
    }

  def getRefreshedAuthDetails(self, appObj, existingToken, tenantObj):
    try:
      val = self.refreshTokenDict.popValue(appObj.getCurDateTime(), existingToken)
    except KeyError:
      return None

    if val['refreshSessionExpiry'] < appObj.getCurDateTime():
      return None

    token = generateRandomRefreshToken(appObj)
    self.refreshTokenDict.addOrReplaceKey(appObj.getCurDateTime(), token, val)
    expiryTime = appObj.getCurDateTime() + timedelta(seconds=int(tenantObj.getRefreshTokenTimeout()))


    userAuthInfo = copy.deepcopy(val['userAuthInformationWithoutJWTorRefreshToken'])
    userAuthInfo['jwtData'] = generateJWTToken(
      appObj=appObj,
      userDict=val['userDict'],
      secret=appObj.APIAPP_JWTSECRET,
      key=val['key'],
      personGUID=val['personGUID'],
      currentlyUsedAuthProviderGuid=val['currentlyUsedAuthProviderGuid'],
      currentlyUsedAuthKey=val['currentlyUsedAuthKey'],
      tenantObj=tenantObj
    )
    userAuthInfo['refresh'] = {
      'token': token,
      'TokenExpiry': expiryTime
    }

    return userAuthInfo
