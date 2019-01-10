# Generate the JWT token to be returned
from datetime import datetime, timedelta
import pytz
import copy
import jwt
from base64 import b64decode
import json

def generateJWTToken(jwtTokenTimeoutDuration, userDict, jwtSecretAndKey):
  expiryTime = datetime.now(pytz.utc) + timedelta(seconds=int(jwtTokenTimeoutDuration))
  
  JWTDict = copy.deepcopy(userDict)
  JWTDict['iss'] = jwtSecretAndKey['key']
  JWTDict['exp'] = jwtSecretAndKey['key']
  encodedJWT = jwt.encode(JWTDict, b64decode(jwtSecretAndKey['secret']), algorithm='HS256')
  return {'JWTToken': encodedJWT.decode('utf-8'), 'TokenExpiry': expiryTime.isoformat() }
