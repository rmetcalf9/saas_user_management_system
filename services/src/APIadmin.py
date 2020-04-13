import APIadmin_Legacy
import APIadmin_Tickets
import constants
from werkzeug.exceptions import Unauthorized

class APIAdminCommonClass():
  #401 = unauthorized -> Goes back to refresh or login makes sense to retry
  #403 = forbidden -> Will not re-prompt for login dosn't make sense to retry
  def verifySecurityOfAdminAPICall(self, appObj, request, tenant, systemAdminRole=constants.masterTenantDefaultSystemAdminRole):
    #Admin api can only be called from masterTenant
    if tenant != constants.masterTenantName:
      raise Unauthorized("Supplied tenant is not the master tenant")

    try:
      return appObj.apiSecurityCheck(
        request=request,
        tenant=tenant,
        requiredRoleList=[constants.DefaultHasAccountRole, systemAdminRole],
        headersToSearch=[constants.jwtHeaderName],
        cookiesToSearch=[constants.jwtCookieName, constants.loginCookieName]
      )
    except constants.invalidPersonInToken as err:
      raise Unauthorized(err.text)
    except constants.invalidUserInToken as err:
      raise Unauthorized(err.text)


def registerAPI(appObj):
  nsAdmin = appObj.flastRestPlusAPIObject.namespace('authed/admin', description='API for accessing admin functions.')

  APIadmin_Legacy.registerAPI(appObj=appObj, APIAdminCommon=APIAdminCommonClass(), nsAdmin=nsAdmin)
  APIadmin_Tickets.registerAPI(appObj=appObj, APIAdminCommon=APIAdminCommonClass(), nsAdmin=nsAdmin)

