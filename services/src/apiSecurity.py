from jwtTokenGeneration import decodeJWTToken
from constants import DefaultHasAccountRole

#Test to see if caller is allowed access to this API

# hasaccount role must always be present for the tenant for access to be verified


def verifyAPIAccessUserLoginRequired(appObj, tenantFromPath, jwttoken, rolesToCheck = []):
  if jwttoken is None:
    return False
  decodedToken = DecodedTokenClass(appObj, jwttoken)
  if not decodedToken.hasRole(tenantFromPath, DefaultHasAccountRole):
    return False
  for k in rolesToCheck:
    if not decodedToken.hasRole(tenantFromPath, k):
      return False
  return True

class DecodedTokenClass():
  tokenData = None
  
  def __init__(self, appObj, jwttoken):
    if (appObj.gateway.ShouldJWTTokensBeVerified()):
      UserID = decodeJWTToken(jwttoken, None, False)['iss']
      jwtSecret = appObj.gateway.GetJWTTokenSecret(UserID)
      self.tokenData = decodeJWTToken(jwttoken, jwtSecret, True)
    else:
      self.tokenData = decodeJWTToken(jwttoken, None, False)

  def hasRole(self, tenant, role):
    if tenant not in self.tokenData['TenantRoles']:
      return False
    if role not in self.tokenData['TenantRoles'][tenant]:
      return False
    return True