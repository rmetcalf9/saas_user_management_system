from datetime import timedelta


def generateRefreshToken(appObj, refreshTokenTimeout):
  expiryTime = appObj.getCurDateTime() + timedelta(seconds=int(refreshTokenTimeout))

  return {
    'token': 'b',
    'TokenExpiry': expiryTime
  }


# Class to hold all the refresh data in memory
class RefreshTokenManager():
  
  def __init__(self, APIAPP_REFRESH_TOKEN_TIMEOUT, APIAPP_REFRESH_SESSION_TIMEOUT):
    pass
    
  def getRefreshedToken(self, appObj, existingToken):
    return None
    
  
  
