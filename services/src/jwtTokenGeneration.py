# Generate the JWT token to be returned
from datetime import timedelta
import copy
import jwt
from base64 import b64decode
import json

def generateJWTToken(appObj, jwtTokenTimeoutDuration, userDict, jwtSecretAndKey, personGUID):
  expiryTime = appObj.getCurDateTime() + timedelta(seconds=int(jwtTokenTimeoutDuration))
  
  JWTDict = copy.deepcopy(userDict)
  JWTDict['authedPersonGuid'] = personGUID
  JWTDict['iss'] = jwtSecretAndKey['key']
  JWTDict['exp'] = expiryTime
  encodedJWT = jwt.encode(JWTDict, b64decode(jwtSecretAndKey['secret']), algorithm='HS256')
  return {'JWTToken': encodedJWT.decode('utf-8'), 'TokenExpiry': expiryTime.isoformat() }
