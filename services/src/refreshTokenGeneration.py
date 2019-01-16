from datetime import timedelta


def generateRefreshToken(appObj, refreshTokenTimeout):
  expiryTime = appObj.getCurDateTime() + timedelta(seconds=int(refreshTokenTimeout))

  return {
    'token': 'b',
    'TokenExpiry': expiryTime
  }
