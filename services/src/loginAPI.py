#This is the publiclly availiable loginAPI

from flask import request
from flask_restplus import Resource, fields
import datetime
import pytz
from baseapp_for_restapi_backend_with_swagger import readFromEnviroment
from werkzeug.exceptions import BadRequest, InternalServerError, Unauthorized #http://werkzeug.pocoo.org/docs/0.14/exceptions/
from constants import customExceptionClass
from apiSharedModels import getTenantModel, getUserModel
from serverInfoAPI import registerServerInfoAPIFn
import copy
from userPersonCommon import GetUser

from tenants import GetTenant, Login, RegisterUser

def getLoginPostDataModel(appObj):
  return appObj.flastRestPlusAPIObject.model('LoginPostData', {
  'authProviderGUID': fields.String(default='DEFAULT', description='Unique identifier of AuthProvider to log in with', required=True),
  'credentialJSON': fields.Raw(description='JSON structure required depends on the Auth Provider type', required=True),
  'identityGUID': fields.String(default='DEFAULT', description='Identity to use to log in with')
  })
def getRefreshPostDataModel(appObj):
  return appObj.flastRestPlusAPIObject.model('RefreshPostData', {
    'token': fields.String(description='Refresh Token that was provided to client')
  })
def getRegisterPostDataModel(appObj):
  return appObj.flastRestPlusAPIObject.model('RegisterPostData', {
  'authProviderGUID': fields.String(default='DEFAULT', description='Unique identifier of AuthProvider to log in with', required=True),
  'credentialJSON': fields.Raw(description='JSON structure required depends on the Auth Provider type', required=True)
  })

#Used with both login response and refresh response
def getLoginResponseModel(appObj):
  jwtTokenModel = appObj.flastRestPlusAPIObject.model('JWTTokenInfo', {
    'JWTToken': fields.String(description='JWTToken'),
    'TokenExpiry': fields.DateTime(dt_format=u'iso8601', description='Time the JWTToken can be used until')
  })
  refreshTokenModel = appObj.flastRestPlusAPIObject.model('RefreshTokenInfo', {
    'token': fields.String(description='Refresh Token'),
    'TokenExpiry': fields.DateTime(dt_format=u'iso8601', description='Time the Refresh token can be used until')
  })
  return appObj.flastRestPlusAPIObject.model('LoginResponseData', {
    'possibleUsers': fields.List(fields.Nested(getUserModel(appObj))),
    'jwtData': fields.Nested(jwtTokenModel, skip_none=True),
    'refresh': fields.Nested(refreshTokenModel, skip_none=True),
    'userGuid': fields.String(description='Unique identifier of user to be used by the application'),
    'authedPersonGuid': fields.String(description='Unique identifier of person for use with Auth APIs'),
    'ThisTenantRoles': fields.List(fields.String(description='Role the user has been assigned for this tenant')),
    'known_as': fields.String(description='User friendly identifier for username'),
    'other_data': fields.Raw(description='Any other data supplied by auth provider', required=True)
  })

def getValidTenantObj(appObj, tenant):
  tenant = GetTenant(appObj, tenant)
  if tenant is None:
    raise BadRequest('Tenant not found')
  return tenant

def registerAPI(appObj):

  nsLogin = appObj.flastRestPlusAPIObject.namespace('public/login', description='Public API for displaying login pages.')
  registerServerInfoAPIFn(appObj, nsLogin)
  
  
  @nsLogin.route('/<string:tenant>/register')
  class register(Resource):
    '''Register'''
    @nsLogin.doc('Register')
    @nsLogin.expect(getRegisterPostDataModel(appObj), validate=True)
    @nsLogin.marshal_with(getUserModel(appObj), skip_none=True)
    @nsLogin.response(201, 'User Registered')
    @nsLogin.response(400, 'Bad Request')
    @nsLogin.response(401, 'Unauthorized')
    def put(self, tenant):
      '''Register'''
      tenantObj = getValidTenantObj(appObj, tenant)
      if 'authProviderGUID' not in request.get_json():
        raise BadRequest('No authProviderGUID provided')
      authProviderGUID = request.get_json()['authProviderGUID']
      if 'credentialJSON' not in request.get_json():
        raise BadRequest('No credentialJSON provided')
      credentialJSON = request.get_json()['credentialJSON']

      try:
        #print("credentialJSON:",credentialJSON)
        #print("loginAPI.py regis - authProviderGUID:",authProviderGUID)
        userObj = RegisterUser(appObj, tenantObj, authProviderGUID, credentialJSON, "loginapi/register")
        
      except customExceptionClass as err:
        if (err.id=='userCreationNotAllowedException'):
          raise Unauthorized(err.text)
        if (err.id=='InvalidAuthConfigException'):
          raise BadRequest(err.text)
        if (err.id=='tryingToCreateDuplicateAuthException'):
          raise BadRequest(err.text)
        if (err.id=='TryingToCreateDuplicateUserException'):
          raise BadRequest(err.text)
          
        raise Exception('InternalServerError')
      except:
        raise 

      returnDict = userObj.getJSONRepresenation(tenant)
      #print("loginAPI returnDict:", returnDict)
      del returnDict["other_data"]
      return returnDict, 201
      
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
        #print("loginAPI.py login - authProviderGUID:",authProviderGUID)
        loginResult = Login(appObj, tenant, authProviderGUID,  request.get_json()['credentialJSON'], requestedUserID='not_valid_guid')
      except customExceptionClass as err:
        if (err.id=='authFailedException'):
          raise Unauthorized('authFailedException')
        if (err.id=='PersonHasNoAccessToAnyIdentitiesException'):
          raise Unauthorized('PersonHasNoAccessToAnyIdentitiesException')
        if (err.id=='authProviderNotFoundException'):
          raise BadRequest('authProviderNotFoundException')
        if (err.id=='InvalidAuthConfigException'):
          raise Unauthorized('Invalid credentials provided')
        raise Exception('InternalServerError')
      except:
        raise InternalServerError

      returnDict = copy.deepcopy(loginResult)
      if returnDict['possibleUserIDs'] is not None:
        #populate possibleUsers from possibleUserIDs
        possibleUsers = []
        for userID in returnDict['possibleUserIDs']:
          possibleUsers.append(GetUser(appObj,userID).getJSONRepresenation(tenant)) #limit roles to only current tenant
        returnDict['possibleUsers'] = possibleUsers

      del returnDict["other_data"]
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

      #possibleUserIDs will always be none
      del refreshedAuthDetails['other_data']
      return refreshedAuthDetails
