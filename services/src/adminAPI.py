#Admin API
from flask import request
from flask_restplus import Resource, fields
from werkzeug.exceptions import Unauthorized
from apiSecurity import verifyAPIAccessUserLoginRequired
from constants import masterTenantDefaultSystemAdminRole, masterTenantName, jwtHeaderName, jwtCookieName

def verifySecurityOfAdminAPICall(appObj, request, tenant):
  #Admin api can only be called from masterTenant
  if tenant != masterTenantName:
    raise Unauthorized()
  
  jwtToken = None
  if jwtHeaderName in request.headers:
    jwtToken = request.headers.get(jwtHeaderName)
  elif jwtCookieName in request.cookies:
    jwtToken = request.cookies.get(jwtCookieName)
  if jwtToken is None:
    raise Unauthorized()

  (verified, decodedToken) = verifyAPIAccessUserLoginRequired(appObj, tenant, jwtToken, [masterTenantDefaultSystemAdminRole])
  if not verified:
    raise Unauthorized()
  
  print(decodedToken)




def registerAPI(appObj):
  nsAdmin = appObj.flastRestPlusAPIObject.namespace('admin', description='API for accessing admin functions.')

  @nsAdmin.route('/<string:tenant>/tenants')
  class tenantInfo(Resource):
  
    '''Admin'''
    @nsAdmin.doc('admin')
    #@nsAdmin.marshal_with(getTenantModel(appObj))
    #@nsAdmin.response(200, 'Success', model=getTenantModel(appObj))
    #@nsAdmin.response(400, 'Bad Request')
    @nsAdmin.response(401, 'Unauthorized')
    def get(self, tenant):
     '''Get list of tenants'''
     verifySecurityOfAdminAPICall(appObj, request, tenant)

     return None

  
