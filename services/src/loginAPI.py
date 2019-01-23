#This is the publiclly availiable loginAPI

from flask import request
from flask_restplus import Resource, fields
import datetime
import pytz
from baseapp_for_restapi_backend_with_swagger import readFromEnviroment
from werkzeug.exceptions import BadRequest, InternalServerError, Unauthorized #http://werkzeug.pocoo.org/docs/0.14/exceptions/
from constants import customExceptionClass
from apiSharedModels import getTenantModel
from serverInfoAPI import registerServerInfoAPIFn

from tenants import GetTenant, Login

def getLoginPostDataModel(appObj):
  return appObj.flastRestPlusAPIObject.model('LoginPostData', {
  'authProviderGUID': fields.String(default='DEFAULT', description='Unique identifier of AuthProvider to log in with', required=True),
  'credentialJSON': fields.Raw(description='JSON structure required depends on the Auth PRovider type', required=True),
  'identityGUID': fields.String(default='DEFAULT', description='Identity to use to log in with')
  })
def getRefreshPostDataModel(appObj):
  return appObj.flastRestPlusAPIObject.model('RefreshPostData', {
    'token': fields.String(description='Refresh Token that was provided to client')
  })

def getLoginResponseModel(appObj):
  possibleIdentityModel = appObj.flastRestPlusAPIObject.model('possibleIdentity', {
    'guid': fields.String(description='Unique identifier for this identity'),
    'userID': fields.String(description='Application unique ID for the user'),
    'name': fields.String(description='Name of this identity'),
    'description': fields.String(description='Description for an identity')
  })
  jwtTokenModel = appObj.flastRestPlusAPIObject.model('JWTTokenInfo', {
    'JWTToken': fields.String(description='JWTToken'),
    'TokenExpiry': fields.DateTime(dt_format=u'iso8601', description='Time the JWTToken can be used until')
  })
  refreshTokenModel = appObj.flastRestPlusAPIObject.model('RefreshTokenInfo', {
    'token': fields.String(description='Refresh Token'),
    'TokenExpiry': fields.DateTime(dt_format=u'iso8601', description='Time the Refresh token can be used until')
  })
  return appObj.flastRestPlusAPIObject.model('LoginResponseData', {
    'possibleIdentities': fields.Nested(possibleIdentityModel, skip_none=True),
    'jwtData': fields.Nested(jwtTokenModel, skip_none=True),
    'refresh': fields.Nested(refreshTokenModel, skip_none=True),
    'userGuid': fields.String(description='Unique identifier of user to be used by the application'),
    'authedPersonGuid': fields.String(description='Unique identifier of person for use with Auth APIs')
  })

#{  
#   "possibleIdentities":"None",
#   "jwtData":{  
#      "JWTToken":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJfQ2hlY2tVc2VySW5pdEFuZFJldHVybkpXVFNlY3JldEFuZEtleV9rZXkiLCJleHAiOjE1NDcyODgyNDMsIlRlbmFudFJvbGVzIjp7InVzZXJzeXN0ZW0iOlsic3lzdGVtYWRtaW4iLCJoYXNhY2NvdW50Il19LCJVc2VySUQiOiJjZGY5YmMyOS1iM2U1LTQ3ZjctYTc4Yi05N2I2YTAwNmYxMjYifQ.-42WuyPYIDDrKHj6ZCIQxWGILbmJ0nDOL4wLOA-rdZU",
#      "TokenExpiry":"2019-01-12T10:17:23.303187+00:00"
#   }
#}
#{
#  "possibleIdentities": [
#    {
#      "guid": "d48b9284-af95-41cc-9dca-e92339c50a12",
#      "userID": "TestUser1",
#      "name": "standard",
#      "description": "standard"
#    },
#    {
#      "guid": "71e8ba49-52d9-48ff-8d93-7b67a8a26274",
#      "userID": "TestUser2",
#      "name": "standard",
#      "description": "standard"
#    }
#  ],
#  "jwtData": null
#}


def getValidTenantObj(appObj, tenant):
  tenant = GetTenant(appObj, tenant)
  if tenant is None:
    raise BadRequest('Tenant not found')
  return tenant

def registerAPI(appObj):

  nsLogin = appObj.flastRestPlusAPIObject.namespace('login', description='Public API for displaying login pages.')
  registerServerInfoAPIFn(appObj, nsLogin)
  
  
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
    @nsLogin.marshal_with(getLoginResponseModel(appObj), skip_none=True)
    @nsLogin.response(200, 'Success', model=getLoginResponseModel(appObj), skip_none=True)
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
        loginResult = Login(appObj, tenant, authProviderGUID,  request.get_json()['credentialJSON'], identityGUID='not_valid_guid')
      except customExceptionClass as err:
        if (err.id=='authFailedException'):
          raise Unauthorized('authFailedException')
        if (err.id=='PersonHasNoAccessToAnyIdentitiesException'):
          raise Unauthorized('PersonHasNoAccessToAnyIdentitiesException')
        if (err.id=='authProviderNotFoundException'):
          raise BadRequest('authProviderNotFoundException')
        if (err.id=='Invalid Auth Config'):
          raise Unauthorized('Invalid credentials provided')
        raise Exception('InternalServerError')
      except:
        raise InternalServerError

      returnDict = loginResult.copy()
      if returnDict['possibleIdentities'] is not None:
        possibleIdentities = []
        for pid in returnDict['possibleIdentities'].keys():
          possibleIdentities.append(returnDict['possibleIdentities'][pid])
        returnDict['possibleIdentities'] = possibleIdentities

      return returnDict

  @nsLogin.route('/<string:tenant>/refresh')
  class refreshAPI(Resource):
    '''Refresh'''
    @nsLogin.doc('refresh')
    @nsLogin.expect(getRefreshPostDataModel(appObj), validate=True)
    @nsLogin.marshal_with(getLoginResponseModel(appObj), skip_none=True)
    @nsLogin.response(200, 'Success', model=getLoginResponseModel(appObj), skip_none=True)
    @nsLogin.response(401, 'Unauthorized')
    def post(self, tenant):
      '''Get new JWT token with Refresh'''
      tenantObj = getValidTenantObj(appObj, tenant)
      refreshedAuthDetails = appObj.refreshTokenManager.getRefreshedAuthDetails(appObj, request.get_json()['token'])
      if refreshedAuthDetails is None:
        raise Unauthorized('Refresh token not found, token or session may have timedout')

      return refreshedAuthDetails
