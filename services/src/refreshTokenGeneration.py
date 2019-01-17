from datetime import timedelta
from expiringdict import expiringdictClass


def generateRefreshToken(appObj, refreshTokenTimeout):
  expiryTime = appObj.getCurDateTime() + timedelta(seconds=int(refreshTokenTimeout))

  return {
    'token': 'b',
    'TokenExpiry': expiryTime
  }


# Class to hold all the refresh data in memory
class RefreshTokenManager():
  refreshTokenDict = None
  
  def __init__(self, appObj, APIAPP_REFRESH_TOKEN_TIMEOUT, APIAPP_REFRESH_SESSION_TIMEOUT):
    self.refreshTokenDict = expiringdictClass(APIAPP_REFRESH_TOKEN_TIMEOUT, appObj.scheduler, appObj.getCurDateTime)

    
  def getRefreshedToken(self, appObj, existingToken):
    return None
    
  
  
