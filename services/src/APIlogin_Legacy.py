#This is the publiclly availiable loginAPI

from flask import request
from flask_restx import Resource, fields, marshal
import datetime
import pytz
from baseapp_for_restapi_backend_with_swagger import readFromEnviroment
from werkzeug.exceptions import BadRequest, InternalServerError, Unauthorized #http://werkzeug.pocoo.org/docs/0.14/exceptions/
from constants import customExceptionClass
from apiSharedModels import getTenantModel, getUserModel, getLoginPostDataModel, getLoginResponseModel
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
    'credentialJSON': fields.Raw(description='JSON structure required depends on the Auth Provider type', required=True),
    'ticket': fields.String(default='DEFAULT', description='If a user has a ticket to grant access')
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

def registerAPI(appObj, nsLogin):

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
        content_raw = request.get_json()
        content = marshal(content_raw, getRegisterPostDataModel(appObj))
        if "ticket" not in content_raw:
          del content["ticket"]
        if content['authProviderGUID'] is None:
          raise BadRequest('No authProviderGUID provided')
        authProviderGUID = content['authProviderGUID']
        if content['credentialJSON'] is None:
          raise BadRequest('No credentialJSON provided')
        credentialJSON = content['credentialJSON']

        try:
          ticketObj = None
          ticketTypeObj = None
          if 'ticket' in content:
            ticketObj = appObj.TicketManager.getTicketObj(ticketGUID=content['ticket'], storeConnection=storeConnection)
            if ticketObj is None:
              raise BadRequest('Invalid Ticket')
            ticketTypeObj = appObj.TicketManager.getTicketType(tenantName=tenant, tickettypeID=ticketObj.getDict()["typeGUID"],storeConnection=storeConnection)
            if ticketTypeObj is None:
              return BadRequest('Invalid Ticket Type')

          def someFn(connectionContext):
            return RegisterUser(appObj, tenantObj, authProviderGUID, credentialJSON, "loginapi/register", connectionContext, ticketObj, ticketTypeObj)
          userObj = storeConnection.executeInsideTransaction(someFn)

        except customExceptionClass as err:
          if (err.id=='userCreationNotAllowedException'):
            raise Unauthorized(err.text)
          if (err.id=='InvalidAuthConfigException'):
            raise BadRequest(err.text)
          if (err.id=='InvalidAuthCredentialsException'):
            raise BadRequest(err.text)
          if (err.id=='tryingToCreateDuplicateAuthException'):
            raise BadRequest(err.text)
          if (err.id=='TryingToCreateDuplicateUserException'):
            raise BadRequest(err.text)
          if (err.id=='ticketNotUsableException'):
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
       #Origin list maintained when tenants are updated
       ##appObj.accessControlAllowOriginObj.addList(tenantObj.getJWTCollectionAllowedOriginList())

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
      content_raw = request.get_json()
      content = marshal(content_raw, getLoginPostDataModel(appObj))

      if content['authProviderGUID'] is None:
        raise BadRequest('No authProviderGUID provided')
      def dbfn(storeConnection):
        tenantObj = getValidTenantObj(appObj, tenant, storeConnection, validateOrigin=True)

        authProviderGUID = content['authProviderGUID']
        UserID = None
        if content['UserID'] is not None:
          UserID = content['UserID']
        ticketObj = None
        ticketTypeObj = None
        if content['ticket'] is not None:
          ticketObj = appObj.TicketManager.getTicketObj(ticketGUID=content['ticket'], storeConnection=storeConnection)
          if ticketObj is None:
            raise BadRequest('Invalid Ticket')
          ticketTypeObj = appObj.TicketManager.getTicketType(tenantName=tenant, tickettypeID=ticketObj.getDict()["typeGUID"],storeConnection=storeConnection)
          if ticketTypeObj is None:
            return BadRequest('Invalid Ticket')

        try:
          #print("APIlogin_Legacy.py login - authProviderGUID:",authProviderGUID)
          def someFn(connectionContext):
            return Login(
              appObj,
              tenant,
              authProviderGUID,
              content['credentialJSON'],
              UserID,
              connectionContext,
              'a','b','c',
              ticketObj=ticketObj,
              ticketTypeObj=ticketTypeObj
            )
          loginResult = storeConnection.executeInsideTransaction(someFn)

        except customExceptionClass as err:
          if (err.id=='authFailedException'):
            raise Unauthorized(err.text)
          if (err.id=='authNotFoundException'):
            raise Unauthorized(err.text)
          if (err.id=='PersonHasNoAccessToAnyIdentitiesException'):
            raise Unauthorized(err.text)
          if (err.id=='authProviderNotFoundException'):
            raise BadRequest(err.text)
          if (err.id=='InvalidAuthConfigException'):
            #import traceback
            #traceback.print_exc()
            raise Unauthorized(err.text)
          if (err.id=='MissingAuthCredentialsException'):
            raise BadRequest(err.text)
          if (err.id=='InvalidAuthCredentialsException'):
            raise BadRequest(err.text)
          if (err.id=='UnknownUserIDException'):
            raise BadRequest(err.text)
          if (err.id=='ExternalAuthProviderNotReachableException'):
            print(err.text)
            raise Exception(err.text)
          if (err.id=='ticketNotUsableException'):
            raise BadRequest(err.text)
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
