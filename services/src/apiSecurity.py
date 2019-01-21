from jwtTokenGeneration import decodeJWTToken
from constants import DefaultHasAccountRole

#Test to see if caller is allowed access to this API

# hasaccount role must always be present for the tenant for access to be verified

def verifyJWTTokenAndReturnAssertions(appObj, jwttoken):
  if (appObj.gateway.ShouldJWTTokensBeVerified()):
    UserID = decodeJWTToken(jwttoken, None, False)['iss']
    jwtSecret = appObj.gateway.GetJWTTokenSecret(UserID)
    return decodeJWTToken(jwttoken, jwtSecret, True)
  else:
    return decodeJWTToken(jwttoken, None, False)

def verifyAPIAccessUserLoginRequired(appObj, tenantFromPath, jwttoken, rolesToCheck = []):
  if jwttoken is None:
    return False
  jwtData = verifyJWTTokenAndReturnAssertions(appObj, jwttoken)
  if tenantFromPath not in jwtData['TenantRoles']:
    return False
  if DefaultHasAccountRole not in jwtData['TenantRoles'][tenantFromPath]:
    return False
  for k in rolesToCheck:
    if k not in jwtData['TenantRoles'][tenantFromPath]:
      return False
  return True

