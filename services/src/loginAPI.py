#This is the publiclly availiable loginAPI

from flask import request
from flask_restplus import Resource, fields
import datetime
import pytz
from baseapp_for_restapi_backend_with_swagger import readFromEnviroment
from werkzeug.exceptions import BadRequest

from tenants import GetTenant

def getTenantModel(appObj):
  AuthProviderModel = appObj.flastRestPlusAPIObject.model('AuthProviderInfo', {
    'Version': fields.String(default='DEFAULT', description='Version of container running on server')
  })
  return appObj.flastRestPlusAPIObject.model('TenantInfo', {
    'Name': fields.String(default='DEFAULT', description='Name and unique identifier of tenant'),
    'Description': fields.String(default='DEFAULT', description='Description of tenant'),
    'AllowUserCreation': fields.Boolean(default=False,description='Allow unknown logins to create new users. (Must be set to true at this level AND AuthPRovider level to work)'),
    'AuthProviders': fields.Nested(AuthProviderModel)
  })  

'''
{
  "Name": "usersystem",
  "Description": "Master Tenant for User Management System", 
  "AllowUserCreation": false, 
  "AuthProviders": {
    "a209bf4f-0761-49b1-9032-a79b31f7ad73": {
      "guid": "a209bf4f-0761-49b1-9032-a79b31f7ad73"
      "AllowUserCreation": false, 
      "IconLink": "aa", 
      "MenuText": "aa", 
      "Type": "internal",
      "ConfigJSON": {
        "userSufix": "@internalDataStore"
      }
    }
  }
}
'''

def getValidTenantObj(appObj, tenant):
  tenant = GetTenant(appObj, tenant)
  if tenant is None:
    raise BadRequest('Tenant not found')
  return tenant

def registerAPI(appObj):

  nsLogin = appObj.flastRestPlusAPIObject.namespace('login', description='Public API for displaying login pages.')
  @nsLogin.route('/<string:tenant>/authproviders')
  class servceInfo(Resource):
  
    '''Login'''
    @nsLogin.doc('login')
    @nsLogin.marshal_with(getTenantModel(appObj))
    @nsLogin.response(200, 'Success', model=getTenantModel(appObj))
    @nsLogin.response(400, 'Bad Request')
    def get(self, tenant):
     '''Get list of auth providers supported by this service'''
     tenantObj = getValidTenantObj(appObj, tenant)
     return tenantObj
     
    
