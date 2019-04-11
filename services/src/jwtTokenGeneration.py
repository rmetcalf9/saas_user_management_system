# Generate the JWT token to be returned
from datetime import timedelta
import copy
import jwt
from base64 import b64decode
import json

def generateJWTToken(appObj, userDict, jwtSecretAndKey, personGUID):
  expiryTime = appObj.getCurDateTime() + timedelta(seconds=int(appObj.APIAPP_JWT_TOKEN_TIMEOUT))
  
  JWTDict = copy.deepcopy(userDict)
  JWTDict['authedPersonGuid'] = personGUID
  JWTDict['iss'] = jwtSecretAndKey['key']
  JWTDict['exp'] = expiryTime
  JWTDict = appObj.gateway.enrichJWTClaims(JWTDict)
  encodedJWT = jwt.encode(JWTDict, b64decode(jwtSecretAndKey['secret']), algorithm='HS256')
  return {'JWTToken': encodedJWT.decode('utf-8'), 'TokenExpiry': expiryTime.isoformat() }

def decodeJWTToken(token, secret, verify):
  if verify:
    return jwt.decode(token, b64decode(secret), algorithms=['HS256'])
  return jwt.decode(token, verify=False)
