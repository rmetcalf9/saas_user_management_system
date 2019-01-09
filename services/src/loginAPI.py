#This is the publiclly availiable loginAPI

from flask import request
from flask_restplus import Resource, fields
import datetime
import pytz
from baseapp_for_restapi_backend_with_swagger import readFromEnviroment
from werkzeug.exceptions import BadRequest, InternalServerError, Unauthorized #http://werkzeug.pocoo.org/docs/0.14/exceptions/
from constants import customExceptionClass

from tenants import GetTenant, Login

def getTenantModel(appObj):
  AuthProviderModel = appObj.flastRestPlusAPIObject.model('AuthProviderInfo', {
    'guid': fields.String(default='abc', description='Unique identifier of AuthProvider'),
    'Type': fields.String(default='internal', description='Authorization provider type'),
    'AllowUserCreation': fields.Boolean(default=False,description='Allow unknown logins to create new users. (Must be set to true at this level AND Tenant level to work)'),   
    'MenuText': fields.String(default='click here', description='Item text used in login method selection screen'),
    'IconLink': fields.String(default=None, description='Image link used in login method selection screen'),
    'ConfigJSON': fields.String(default=None, description='Extra configuration required per auth type')
  })
  return appObj.flastRestPlusAPIObject.model('TenantInfo', {
    'Name': fields.String(default='DEFAULT', description='Name and unique identifier of tenant'),
    'Description': fields.String(default='DEFAULT', description='Description of tenant'),
    'AllowUserCreation': fields.Boolean(default=False,description='Allow unknown logins to create new users. (Must be set to true at this level AND AuthPRovider level to work)'),
    'AuthProviders': fields.List(fields.Nested(AuthProviderModel))
  })  

def getLoginPostDataModel(appObj):
  return appObj.flastRestPlusAPIObject.model('LoginPostData', {
  'authProviderGUID': fields.String(default='DEFAULT', description='Unique identifier of AuthProvider to log in with', required=True),
  'credentialJSON': fields.Raw(description='JSON structure required depends on the Auth PRovider type', required=True),
  'identityGUID': fields.String(default='DEFAULT', description='Identity to use to log in with')
  })

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
     return tenantObj.getJSONRepresenation()
     
    '''Login'''
    @nsLogin.doc('login')
    @nsLogin.expect(getLoginPostDataModel(appObj), validate=True)
    @nsLogin.marshal_with(getTenantModel(appObj))
    @nsLogin.response(200, 'Success', model=getTenantModel(appObj))
    @nsLogin.response(400, 'Bad Request')
    @nsLogin.response(401, 'Unauthorized')
    def post(self, tenant):
     '''Login and recieve JWT token'''
     tenantObj = getValidTenantObj(appObj, tenant)
     if 'authProviderGUID' not in request.get_json():
       raise BadRequest('No authProviderGUID provided')
     authProviderGUID = request.get_json()['authProviderGUID']
     identityGUID = None
     if 'identityGUID' in request.get_json():
       identityGUID = request.get_json()['identityGUID']
     
     try:
       userInfo = Login(appObj, tenant, authProviderGUID,  request.get_json()['credentialJSON'], identityGUID='not_valid_guid')
     except customExceptionClass as err:
       if (err.id=='authFailedException'):
         raise Unauthorized('authFailedException')
       if (err.id=='PersonHasNoAccessToAnyIdentitiesException'):
         raise Unauthorized('PersonHasNoAccessToAnyIdentitiesException')
       if (err.id=='authProviderNotFoundException'):
         raise BadRequest('authProviderNotFoundException')
       raise ('InternalServerError')
     except:
       raise InternalServerError
     return userInfo

