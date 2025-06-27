# Generate the JWT token to be returned
from datetime import timedelta
import copy
import jwt
from base64 import b64decode
import json

def generateJWTToken(appObj, userDict, secret, key, personGUID, currentlyUsedAuthProviderGuid, currentlyUsedAuthKey):
  expiryTime = appObj.getCurDateTime() + timedelta(seconds=int(appObj.APIAPP_JWT_TOKEN_TIMEOUT))
  if secret is None:
    raise Exception("Trying to generate a JWT Token without a secret being set")
  if key is None:
    raise Exception("Trying to generate a JWT Token without a key being set")
  
  
  JWTDict = copy.deepcopy(userDict)
  JWTDict['authedPersonGuid'] = personGUID
  JWTDict['currentlyUsedAuthProviderGuid'] = currentlyUsedAuthProviderGuid
  JWTDict['currentlyUsedAuthKey'] = currentlyUsedAuthKey
  JWTDict['iss'] = key
  JWTDict['exp'] = expiryTime
  JWTDict = appObj.gateway.enrichJWTClaims(JWTDict)
  encodedJWT = jwt.encode(JWTDict, b64decode(secret), algorithm='HS256')
  return {'JWTToken': encodedJWT, 'TokenExpiry': expiryTime.isoformat() }
