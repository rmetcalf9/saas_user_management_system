#Admin API
from flask import request
from flask_restplus import Resource, fields
from werkzeug.exceptions import Unauthorized
##from apiSecurity import verifySecurityOfAPICall

def verifySecurityOfAdminAPICall(appObj, request, tenant):
  raise Unauthorized()




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
     verifySecurityOfAPICall(appObj, request, tenant)

     return None

  
