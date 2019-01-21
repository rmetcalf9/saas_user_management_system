


#Test to see if caller is allowed access to this API

# hasaccount role must always be present for the tenant for access to be verified

def verifyAPIAccessUserLoginRequired(tenantFromPath, jwttoken):
  return False

