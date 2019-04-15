# Generate the JWT token to be returned
from datetime import timedelta
import copy
import jwt
from base64 import b64decode
import json

def generateJWTToken(appObj, userDict, secret, key, personGUID):
  expiryTime = appObj.getCurDateTime() + timedelta(seconds=int(appObj.APIAPP_JWT_TOKEN_TIMEOUT))
  if secret is None:
    raise Exception("Trying to generate a JWT Token without a secret being set")
  if key is None:
    raise Exception("Trying to generate a JWT Token without a key being set")
  
  JWTDict = copy.deepcopy(userDict)
  JWTDict['authedPersonGuid'] = personGUID
  JWTDict['iss'] = key
  JWTDict['exp'] = expiryTime
  JWTDict = appObj.gateway.enrichJWTClaims(JWTDict)
  encodedJWT = jwt.encode(JWTDict, b64decode(secret), algorithm='HS256')
  return {'JWTToken': encodedJWT.decode('utf-8'), 'TokenExpiry': expiryTime.isoformat() }

def decodeJWTToken(token, secret, verify):
  if verify:
    return jwt.decode(token, b64decode(secret), algorithms=['HS256'])
  return jwt.decode(token, verify=False)
