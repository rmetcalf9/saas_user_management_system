#currentAuth API
from flask import request
from flask_restplus import Resource
from constants import jwtHeaderName, jwtCookieName, loginCookieName
'''
The currentAuth API includes functionality availiable for authed users

Security:
 - they do not need an has account role for the tenant
'''



#401 = unauthorized -> Goes back to refresh or login makes sense to retry
#403 = forbidden -> Will not re-prompt for login dosn't make sense to retry
def verifySecurityOfAPICall(appObj, request, tenant):
  requiredRoles = []
  
  return appObj.apiSecurityCheck(
    request, 
    tenant, 
    requiredRoles, 
    [jwtHeaderName], 
    [jwtCookieName, loginCookieName]
  )

  
def registerAPI(appObj):
  nsCurAuth = appObj.flastRestPlusAPIObject.namespace('authed/currentAuth', description='API for accessing functions for the currently authed user/person.')

  @nsCurAuth.route('/<string:tenant>/currentAuthInfo')
  class currentAuthInfo(Resource):
    '''Current Auth Info'''
    @nsCurAuth.doc('currentAuthInfo')
    #@nsCurAuth.marshal_with(getSecurityTestResultModel(appObj))
    #@nsCurAuth.response(200, 'Success', model=getSecurityTestResultModel(appObj))
    @nsCurAuth.response(401, 'Unauthorized')
    @nsCurAuth.response(403, 'Forbidden - User dosen\'t have required role')
    @appObj.addStandardSortParams(nsCurAuth)
    def get(self, tenant):
      '''Get list of tenants'''
      verifySecurityOfAPICall(appObj, request, tenant)
      return {
        'TODO': 'TODO'
      }
