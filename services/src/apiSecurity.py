from constants import DefaultHasAccountRole
from werkzeug.exceptions import Unauthorized, Forbidden, BadRequest, InternalServerError, NotFound, Conflict
import jwt
from base64 import b64decode

#Test to see if caller is allowed access to this API

def _getFromHeader(request, headers):
  for h in headers:
    if h in request.headers:
      token = request.headers.get(h)
      return token
  return None
  
def _getFromLoginCookie(request, cookies):
  for c in cookies:
    if c in request.cookies:
      cookie = request.cookies.get(c)
      try:
        a = unquote(cookie)
        a = json.loads(a)
        if 'jwtData' in a.keys():
          if 'JWTToken' in a['jwtData']:
            return a['jwtData']['JWTToken']
      except:
        pass
  return None

def _getFromNormCookie(request, cookies):
  for c in cookies:
    if c in request.cookies:
      return request.cookies.get(c)

def apiSecurityCheck(request, tenant, requiredRoleList, headersToSearch, cookiesToSearch, jwtSecret):
  jwtToken = _getFromHeader(request, headersToSearch)
  if jwtToken is None:
    jwtToken = _getFromLoginCookie(request, cookiesToSearch)
    if jwtToken is None:
      jwtToken = _getFromNormCookie(request, cookiesToSearch)
      if jwtToken is None:
        raise Unauthorized("No JWT Token in header or cookie")
  
  try:
    decodedJWTToken = DecodedTokenClass(jwtSecret, jwtToken)
  except jwt.InvalidSignatureError:
    raise Unauthorized("InvalidSignatureError")
  except jwt.ExpiredSignatureError:
    raise Unauthorized("ExpiredSignatureError")
  except Exception as err:
    raise Unauthorized("Problem with token - " + err)

  for x in requiredRoleList:
    if not decodedJWTToken.hasRole(tenant, x):
      raise Forbidden("Missing required Role")

  return decodedJWTToken

def decodeJWTToken(token, secret, verify):
  if verify:
    return jwt.decode(token, b64decode(secret), algorithms=['HS256'])
  return jwt.decode(token, verify=False)

  
class DecodedTokenClass():
  _tokenData = None
  
  def __init__(self, jwtSecret, jwttoken):
    if jwtSecret is None:
      raise Exception('Unable to verify JWT token as APIAPP_JWTSECRET is not set')
      
    #Does two decodes, one without verification
    ## this means we can read the userID
    UserID = decodeJWTToken(jwttoken, None, False)['iss']
    self._tokenData = decodeJWTToken(jwttoken, jwtSecret, True)

  def hasRole(self, tenant, role):
    if tenant not in self._tokenData['TenantRoles']:
      return False
    if role not in self._tokenData['TenantRoles'][tenant]:
      return False
    return True
    
  def getUserID(self):
    return self._tokenData["UserID"]
    
  def getPersonID(self):
    return self._tokenData["authedPersonGuid"]