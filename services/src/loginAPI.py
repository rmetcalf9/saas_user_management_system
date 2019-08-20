#This is the publiclly availiable loginAPI

from flask import request
from flask_restplus import Resource, fields
import datetime
import pytz
from baseapp_for_restapi_backend_with_swagger import readFromEnviroment
from werkzeug.exceptions import BadRequest, InternalServerError, Unauthorized #http://werkzeug.pocoo.org/docs/0.14/exceptions/
from constants import customExceptionClass
from apiSharedModels import getTenantModel, getUserModel, getLoginPostDataModel, getLoginResponseModel
from serverInfoAPI import registerServerInfoAPIFn
import copy
from userPersonCommon import GetUser

from tenants import GetTenant, Login, RegisterUser

def getRefreshPostDataModel(appObj):
  return appObj.flastRestPlusAPIObject.model('RefreshPostData', {
    'token': fields.String(description='Refresh Token that was provided to client')
  })
def getRegisterPostDataModel(appObj):
  return appObj.flastRestPlusAPIObject.model('RegisterPostData', {
  'authProviderGUID': fields.String(default='DEFAULT', description='Unique identifier of AuthProvider to log in with', required=True),
  'credentialJSON': fields.Raw(description='JSON structure required depends on the Auth Provider type', required=True)
  })

def getValidTenantObj(appObj, tenant, storeConnection, validateOrigin):
  tenantObj = GetTenant(tenant, storeConnection, appObj=appObj)
  if tenantObj is None:
    raise BadRequest('Tenant not found')
  if validateOrigin:
    originHeader = request.headers.get('Origin')
    if originHeader not in tenantObj.getJWTCollectionAllowedOriginList():
      raise Unauthorized('Invalid Origin')
  return tenantObj

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
      def dbfn(storeConnection):
        tenantObj = getValidTenantObj(appObj, tenant, storeConnection, validateOrigin=True)
        if 'authProviderGUID' not in request.get_json():
          raise BadRequest('No authProviderGUID provided')
        authProviderGUID = request.get_json()['authProviderGUID']
        if 'credentialJSON' not in request.get_json():
          raise BadRequest('No credentialJSON provided')
        credentialJSON = request.get_json()['credentialJSON']

        try:
          #print("credentialJSON:",credentialJSON)
          #print("loginAPI.py regis - authProviderGUID:",authProviderGUID)
          def someFn(connectionContext):
            return RegisterUser(appObj, tenantObj, authProviderGUID, credentialJSON, "loginapi/register", connectionContext)
          userObj = storeConnection.executeInsideTransaction(someFn)

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
      return appObj.objectStore.executeInsideConnectionContext(dbfn)

  @nsLogin.route('/<string:tenant>/authproviders')
  class servceInfo(Resource):

    '''Get Auth Providers'''
    @nsLogin.doc('login')
    @nsLogin.marshal_with(getTenantModel(appObj))
    @nsLogin.response(200, 'Success', model=getTenantModel(appObj))
    @nsLogin.response(400, 'Bad Request')
    def get(self, tenant):
     '''Get list of auth providers supported by this service'''
     def dbfn(storeConnection):
       tenantObj = getValidTenantObj(appObj, tenant, storeConnection, validateOrigin=False)
       appObj.accessControlAllowOriginObj.addList(tenantObj.getJWTCollectionAllowedOriginList())

       #print(tenantObj.getJSONRepresenation())
       return tenantObj.getJSONRepresenation()
     return appObj.objectStore.executeInsideConnectionContext(dbfn)

    '''Login'''
    @nsLogin.doc('login')
    @nsLogin.expect(getLoginPostDataModel(appObj), validate=True)
    @nsLogin.marshal_with(getLoginResponseModel(appObj), skip_none=True)
    @nsLogin.response(200, 'Success', model=getLoginResponseModel(appObj), skip_none=True)
    @nsLogin.response(400, 'Bad Request')
    @nsLogin.response(401, 'Unauthorized')
    def post(self, tenant):
      '''Login and recieve JWT token'''
      if 'authProviderGUID' not in request.get_json():
        raise BadRequest('No authProviderGUID provided')
      def dbfn(storeConnection):
        tenantObj = getValidTenantObj(appObj, tenant, storeConnection, validateOrigin=True)

        authProviderGUID = request.get_json()['authProviderGUID']
        UserID = None
        if 'UserID' in request.get_json():
          UserID = request.get_json()['UserID']

        try:
          #print("loginAPI.py login - authProviderGUID:",authProviderGUID)
          def someFn(connectionContext):
            return Login(
              appObj,
              tenant,
              authProviderGUID,
              request.get_json()['credentialJSON'],
              UserID,
              connectionContext, 'a','b','c'
            )
          loginResult = storeConnection.executeInsideTransaction(someFn)

        except customExceptionClass as err:
          if (err.id=='authFailedException'):
            raise Unauthorized('authFailedException')
          if (err.id=='authNotFoundException'):
            raise Unauthorized('authFailedException')
          if (err.id=='PersonHasNoAccessToAnyIdentitiesException'):
            raise Unauthorized('PersonHasNoAccessToAnyIdentitiesException')
          if (err.id=='authProviderNotFoundException'):
            raise BadRequest('authProviderNotFoundException')
          if (err.id=='InvalidAuthConfigException'):
            raise Unauthorized('Invalid credentials provided')
          if (err.id=='UnknownUserIDException'):
            raise BadRequest(err.text)
          if (err.id=='ExternalAuthProviderNotReachableException'):
            print(err.text)
            raise Exception('ExternalAuthProviderNotReachable')
          raise Exception('InternalServerError')
        except:
          raise InternalServerError

        returnDict = copy.deepcopy(loginResult)
        if returnDict['possibleUserIDs'] is not None:
          #populate possibleUsers from possibleUserIDs
          possibleUsers = []
          for userID in returnDict['possibleUserIDs']:
            possibleUsers.append(GetUser(appObj,userID,storeConnection).getJSONRepresenation(tenant)) #limit roles to only current tenant
          returnDict['possibleUsers'] = possibleUsers

        del returnDict["other_data"]
        return returnDict
      return appObj.objectStore.executeInsideConnectionContext(dbfn)

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
      def dbfn(storeConnection):
        #This is the important call where other app will call
        tenantObj = getValidTenantObj(appObj, tenant, storeConnection, validateOrigin=True)

        refreshedAuthDetails = appObj.refreshTokenManager.getRefreshedAuthDetails(appObj, request.get_json()['token'])
        if refreshedAuthDetails is None:
          raise Unauthorized('Refresh token not found, token or session may have timedout')

        #possibleUserIDs will always be none
        del refreshedAuthDetails['other_data']
        return refreshedAuthDetails
      return appObj.objectStore.executeInsideConnectionContext(dbfn)
