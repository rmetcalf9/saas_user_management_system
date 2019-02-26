from jwtTokenGeneration import decodeJWTToken
from constants import DefaultHasAccountRole

#Test to see if caller is allowed access to this API

# hasaccount role must always be present for the tenant for access to be verified

#Return PArams (1,2,3)
# 1 = True to allow user through (login is valid and role is present)
# 2 = When True this includes the decoded token
# 3 = Forbidden? True if the users token is ok but the role is missing, false otherwise
def verifyAPIAccessUserLoginRequired(appObj, tenantFromPath, jwttoken, rolesToCheck = []):
  if jwttoken is None:
    return False, None, False
  decodedToken = DecodedTokenClass(appObj, jwttoken)
  if not decodedToken.hasRole(tenantFromPath, DefaultHasAccountRole):
    return False, None, False
  for k in rolesToCheck:
    if not decodedToken.hasRole(tenantFromPath, k):
      return False, None, True #Requested role is missing
  return True, decodedToken, False

class DecodedTokenClass():
  _tokenData = None
  
  def __init__(self, appObj, jwttoken):
    if (appObj.gateway.ShouldJWTTokensBeVerified()):
      UserID = decodeJWTToken(jwttoken, None, False)['iss']
      jwtSecret = appObj.gateway.GetJWTTokenSecret(UserID)
      self._tokenData = decodeJWTToken(jwttoken, jwtSecret, True)
    else:
      self._tokenData = decodeJWTToken(jwttoken, None, False)

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