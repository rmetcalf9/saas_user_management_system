#Admin API
from flask import request
from flask_restx import Resource, fields, marshal
from werkzeug.exceptions import BadRequest, InternalServerError, NotFound, Conflict
from constants import masterTenantDefaultSystemAdminRole, masterTenantName, jwtHeaderName, jwtCookieName, loginCookieName, ShouldNotSupplySaltWhenCreatingAuthProvException, objectVersionHeaderName, DefaultHasAccountRole, customExceptionClass
import AuthProviders
import constants
from apiSharedModels import getTenantModel, getUserModel, getPersonModel, getAuthProviderModel
from urllib.parse import unquote
import json
from tenants import CreateTenant, UpdateTenant, DeleteTenant, GetTenant, AddAuthForUser
from AuthProviders.authsCommon import getAuthRecord
from userPersonCommon import GetUser, CreateUserObjFromUserDict, RemoveUserAssociation
from users import GetPaginatedUserData, UpdateUser, DeleteUser, CreateUser, associateUserWithPerson
from persons import GetPaginatedPersonData, CreatePerson, GetPerson, UpdatePerson, DeletePerson, CreatePersonObjFromUserDict, deleteAuthAndUnassiciateFromPerson
from tenantObj import tenantClass
from object_store_abstraction import WrongObjectVersionExceptionClass
import copy
import base64

import logging
logger = logging.getLogger(__name__)
###logger.setLevel(logging.INFO)


def getPaginatedParamValues(request):
  #value checking now done in object store
  offset = request.args.get('offset')
  pagesize = request.args.get('pagesize')
  sort = request.args.get('sort')
  query = request.args.get('query')
  return {
    'offset': offset,
    'pagesize': pagesize,
    'query': query,
    'sort': sort,
  }

def updateContentConvertingInputStringsToDictsWhereRequired(content):
  if 'AuthProviders' in content:
    for curAuthProvider in content['AuthProviders']:
      if 'ConfigJSON' in curAuthProvider:
        if not isinstance(curAuthProvider['ConfigJSON'],dict):
          curAuthProvider['ConfigJSON'] = json.loads(curAuthProvider['ConfigJSON'])
          #print("updateContentConvertingInputStringsToDictsWhereRequired:",curAuthProvider['ConfigJSON'])
  return content

def getCreateTenantModel(appObj):
  return appObj.flastRestPlusAPIObject.model('CreateTenantInfo', {
    'Name': fields.String(default='DEFAULT', description='Name and unique identifier of tenant'),
    'Description': fields.String(default='DEFAULT', description='Description of tenant'),
    'AllowUserCreation': fields.Boolean(default=False,description='Allow unknown logins to create new users. (Must be set to true at this level AND AuthPRovider level to work)'),
    'AuthProviders': fields.List(fields.Nested(getAuthProviderModel(appObj))),
    'JWTCollectionAllowedOriginList': fields.List(fields.String(default='DEFAULT', description='Allowed origin to retrieve JWT tokens from')),
    'TicketOverrideURL': fields.String(default='', description='Overrider URL for tickets'),
    'TenantBannerHTML': fields.String(default='', description='HTML displayed in select auth and login screens'),
    'SelectAuthMessage': fields.String(default='', description='Message displayed above buttons in select auth screen')
  })

def getCreateUserModel(appObj):
  return appObj.flastRestPlusAPIObject.model('CreateUserInfo', {
    'UserID': fields.String(default='DEFAULT', description='Unique identifier of User'),
    'known_as': fields.String(description='User friendly identifier for username'),
    'mainTenant': fields.String(description='If set then a hasaccount role is setup for this tenant'),
  })

def getCreatePersonModel(appObj):
  return appObj.flastRestPlusAPIObject.model('CreatePersonInfo', {
  })


def getUserPersonLinkModel(appObj):
  return appObj.flastRestPlusAPIObject.model('UserPersonLinkInfo', {
    'UserID': fields.String(default='DEFAULT', description='Unique identifier of User'),
    'personGUID': fields.String(default='DEFAULT', description='Unique identifier of Person')
  })

def getCreateAuthModel(appObj):
  return appObj.flastRestPlusAPIObject.model('CreateAuthInfo', {
    'personGUID': fields.String(default='DEFAULT', description='Unique identifier of Person', required=True),
    'tenantName': fields.String(description='Name of Tenant'),
    'authProviderGUID': fields.String(default='DEFAULT', description='Unique identifier of Person', required=True),
    'credentialJSON': fields.Raw(description='JSON structure required depends on the Auth Provider type', required=True),
  })

def getAuthModel(appObj):
  return appObj.flastRestPlusAPIObject.model('AuthInfo', {
    'personGUID': fields.String(default='DEFAULT', description='Unique identifier of Person', required=True),
    'tenantName': fields.String(description='Name of Tenant'),
    'authProviderGUID': fields.String(default='DEFAULT', description='Unique identifier of Person', required=True),
    'AuthUserKey': fields.String(default='DEFAULT', description='Unique identifier of Auth'),
  })

def getSecurityTestResultModel(appObj):
  return appObj.flastRestPlusAPIObject.model('SecurityTestResultInfo', {
    'result': fields.String(default='DEFAULT', description='Pass', required=True)
  })

def requiredInPayload(content, fieldList):
  for a in fieldList:
    if a not in content:
      raise BadRequest(a + ' not in payload')

def registerAPI(appObj, APIAdminCommon, nsAdmin):
  @nsAdmin.route('/<string:tenant>/securityTestEndpoint')
  class securityTesting(Resource):
    '''Admin'''
    @nsAdmin.doc('admin')
    @nsAdmin.marshal_with(getSecurityTestResultModel(appObj))
    @nsAdmin.response(200, 'Success', model=getSecurityTestResultModel(appObj))
    @nsAdmin.response(401, 'Unauthorized')
    @nsAdmin.response(403, 'Forbidden - User dosen\'t have required role')
    @appObj.addStandardSortParams(nsAdmin)
    def get(self, tenant):
      '''Get list of tenants'''
      APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant, constants.SecurityEndpointAccessRole)
      return {
        'result': 'pass'
      }

  @nsAdmin.route('/<string:tenant>/tenants')
  class tenantsInfo(Resource):

    '''Admin'''
    @nsAdmin.doc('admin')
    @nsAdmin.marshal_with(appObj.getResultModel(getTenantModel(appObj)))
    @nsAdmin.response(200, 'Success', model=appObj.getResultModel(getTenantModel(appObj)))
    @nsAdmin.response(401, 'Unauthorized')
    @nsAdmin.response(403, 'Forbidden - User dosen\'t have required role')
    @appObj.addStandardSortParams(nsAdmin)
    def get(self, tenant):
      '''Get list of tenants'''
      APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)

      paginatedParamValues = getPaginatedParamValues(request)

      def defOutput(item):
        return tenantClass(item[0],item[1], appObj).getJSONRepresenation()

      try:
        def dbfn(storeConnection):
          outputFN = defOutput
          return storeConnection.getPaginatedResult("tenants", paginatedParamValues, outputFN)
        return appObj.objectStore.executeInsideConnectionContext(dbfn)
      except:
        raise InternalServerError


    @nsAdmin.doc('post Tenant')
    @nsAdmin.expect(getCreateTenantModel(appObj), validate=True)
    @appObj.flastRestPlusAPIObject.response(400, 'Validation error')
    @appObj.flastRestPlusAPIObject.response(201, 'Created')
    @appObj.flastRestPlusAPIObject.marshal_with(getTenantModel(appObj), code=200, description='Tenant created', skip_none=True)
    @nsAdmin.response(403, 'Forbidden - User dosen\'t have required role')
    def post(self, tenant):
      '''Create Tenant'''
      APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)
      content_raw = request.get_json()
      content = marshal(content_raw, getCreateTenantModel(appObj))
      requiredInPayload(content, ['Name','Description','AllowUserCreation'])
      if "AuthProviders" in content:
        if content["AuthProviders"] is not None:
          if len(content["AuthProviders"]) != 0:
            raise BadRequest("Not possible to create a Tenant with AuthProviders ")
      try:
        def someFn(connectionContext):
          return CreateTenant(appObj, content['Name'], content['Description'], content['AllowUserCreation'],
            connectionContext,
            JWTCollectionAllowedOriginList=getOrSomethngElse("JWTCollectionAllowedOriginList",content, []),
            TicketOverrideURL=getOrSomethngElse("TicketOverrideURL",content, ""),
            TenantBannerHTML=getOrSomethngElse("TenantBannerHTML",content, ""),
            SelectAuthMessage=getOrSomethngElse("SelectAuthMessage",content, "How do you want to verify who you are?")
          )
        tenantObj = appObj.objectStore.executeInsideTransaction(someFn)

      except customExceptionClass as err:
        if (err.id=='tenantAlreadtExistsException'):
          raise BadRequest(err.text)
        raise Exception('InternalServerError')
      except:
        raise InternalServerError

      return tenantObj.getJSONRepresenation(), 201

  def getOrSomethngElse(ite, lis, somethingElse):
    if ite not in lis:
      return somethingElse
    if lis[ite] is None:
      return somethingElse
    return lis[ite]

  @nsAdmin.route('/<string:tenant>/tenants/<string:tenantName>')
  class tenantInfo(Resource):

    '''Admin'''
    @nsAdmin.doc('get Tenant')
    @nsAdmin.marshal_with(getTenantModel(appObj))
    @nsAdmin.response(200, 'Success', model=getTenantModel(appObj))
    @nsAdmin.response(401, 'Unauthorized')
    @nsAdmin.response(403, 'Forbidden - User dosen\'t have required role')
    @nsAdmin.response(404, 'Tenant Not Found')
    def get(self, tenant, tenantName):
      '''Get tenant information'''
      APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)
      def dbfn(storeConnection):
        a = GetTenant(tenantName, storeConnection, appObj=appObj)
        if a is None:
          raise NotFound('Tenant Not Found')
        return a.getJSONRepresenation()
      return appObj.objectStore.executeInsideConnectionContext(dbfn)

    @nsAdmin.doc('update Tenant')
    @nsAdmin.expect(getTenantModel, validate=True)
    @nsAdmin.response(200, 'Tenant Updated')
    @nsAdmin.response(400, 'Validation Error')
    @appObj.flastRestPlusAPIObject.marshal_with(getTenantModel(appObj), code=200, description='Tenant updated')
    def put(self, tenant, tenantName):
      '''Update Tenant'''
      APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)
      content_raw = request.get_json()
      content = marshal(content_raw, getTenantModel(appObj))
      if "ObjectVersion" not in content_raw:
        del content["ObjectVersion"]

      requiredInPayload(content, ['Name','Description','AllowUserCreation','AuthProviders','ObjectVersion'])
      resp = None
      try:
        content = updateContentConvertingInputStringsToDictsWhereRequired(content)
        def someFn(connectionContext):
          return UpdateTenant(
            appObj, content['Name'],
            content['Description'],
            content['AllowUserCreation'],
            content['AuthProviders'],
            content['ObjectVersion'], connectionContext,
            JWTCollectionAllowedOriginList=getOrSomethngElse("JWTCollectionAllowedOriginList",content, None),
            TicketOverrideURL=getOrSomethngElse("TicketOverrideURL",content, ""),
            TenantBannerHTML=getOrSomethngElse("TenantBannerHTML", content, ""),
            SelectAuthMessage=getOrSomethngElse("SelectAuthMessage", content, "How do you want to verify who you are?")
          )
        tenantObj = appObj.objectStore.executeInsideTransaction(someFn)

        resp = tenantObj.getJSONRepresenation()

      except customExceptionClass as err:
        if (err.id=='tenantDosentExistException'):
          raise BadRequest(err.text)
        if (err.id=='ShouldNotSupplySaltWhenCreatingAuthProvException'):
          raise BadRequest(err.text)
        if (err.id=='cantUpdateExistingAuthProvException'):
          raise BadRequest(err.text)
        raise Exception('InternalServerError')
      except AuthProviders.CustomAuthProviderExceptionClass as err:
        if (err.id=='InvalidAuthConfigException'):
          raise BadRequest(err.text)
        if (err.id == 'authProviderNotFoundException'):
          raise BadRequest(err.text)
        raise Exception('InternalServerError')
      except KeyError as err:
        raise BadRequest(str(err))
        #raise err
      except WrongObjectVersionExceptionClass as err:
        raise Conflict(str(err))
      except Exception as err:
        print("Un catagoarised exception")
        print(str(err))
        raise InternalServerError

      return resp

    @nsAdmin.doc('delete Tenant')
    @nsAdmin.response(200, 'Tenant Deleted')
    @nsAdmin.response(400, 'Error')
    @nsAdmin.response(403, 'Forbidden - User dosen\'t have required role')
    @nsAdmin.response(409, 'Conflict')
    @appObj.flastRestPlusAPIObject.marshal_with(getTenantModel(appObj), code=200, description='Tenant Deleted')
    def delete(self, tenant, tenantName):
      '''Delete Tenant'''
      APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)
      objectVersion = None
      if objectVersionHeaderName in request.headers:
        objectVersion = request.headers.get(objectVersionHeaderName)
      if objectVersion is None:
        raise BadRequest(objectVersionHeaderName + " header missing")
      try:
        def someFn(connectionContext):
          tenantObj = DeleteTenant(appObj, tenantName, objectVersion, connectionContext)
          return tenantObj.getJSONRepresenation()
        return appObj.objectStore.executeInsideTransaction(someFn)
      except customExceptionClass as err:
        if (err.id=='tenantDosentExistException'):
          raise BadRequest(err.text)
        if (err.id=='cantDeleteMasterTenantException'):
          raise BadRequest(err.text)
        raise Exception('InternalServerError')
      except WrongObjectVersionExceptionClass as err:
        raise Conflict(str(err))
      except:
        raise InternalServerError

  @nsAdmin.route('/<string:tenant>/users')
  class usersInfo(Resource):

    '''Admin'''
    @nsAdmin.doc('admin')
    @nsAdmin.marshal_with(appObj.getResultModel(getUserModel(appObj)))
    @nsAdmin.response(200, 'Success', model=appObj.getResultModel(getUserModel(appObj)))
    @nsAdmin.response(401, 'Unauthorized')
    @nsAdmin.response(403, 'Forbidden - User dosen\'t have required role')
    @appObj.addStandardSortParams(nsAdmin)
    def get(self, tenant):
      '''Get list of users'''
      #logger.info('ADMIN/users A - request.args:' + str(request.args))
      #print('ADMIN/users A - request.args:' + str(request.args))
      #print('              - request.values:' + str(request.values))
      #print('              - request.url:' + str(request.url))
      APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)
      paginatedParamValues = getPaginatedParamValues(request)
      #print(str(paginatedParamValues))

      def dbfn(storeConnection):
        def defOutput(item):
          #print("getUSERSPaginated DEBUG - item[0]=", item[0])
          a = CreateUserObjFromUserDict(appObj, item[0],item[1],item[2],item[3], storeConnection).getJSONRepresenation()
          ##print("a:", a)
          return a

        try:
          outputFN = defOutput
          ##print(a)

          return GetPaginatedUserData(appObj, paginatedParamValues, outputFN, storeConnection)
        except Exception as e:
          print(e)
          print(str(e.args))
          print(e.args)
          raise InternalServerError
      return appObj.objectStore.executeInsideConnectionContext(dbfn)

    @nsAdmin.doc('post User')
    @nsAdmin.expect(getCreateUserModel(appObj), validate=True)
    @appObj.flastRestPlusAPIObject.response(400, 'Validation error')
    @appObj.flastRestPlusAPIObject.response(201, 'Created')
    @appObj.flastRestPlusAPIObject.marshal_with(getUserModel(appObj), code=200, description='User created', skip_none=True)
    @nsAdmin.response(403, 'Forbidden - User dosen\'t have required role')
    def post(self, tenant):
      '''Create User'''
      APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)
      content_raw = request.get_json()
      content = marshal(content_raw, getCreateUserModel(appObj))
      requiredInPayload(content, ['UserID','known_as'])
      userData = {
        "user_unique_identifier": content["UserID"],
        "known_as": content["known_as"]
      }
      def dbfn(storeConnection):
        tenant = None
        if content["mainTenant"] is not None:
          if content["mainTenant"] != "":
            tenant = content["mainTenant"]
            tenantObj = GetTenant(tenant, storeConnection, appObj=appObj)
            if tenantObj is None:
              raise BadRequest("Invalid tenant name")
        try:
          def someFn(connectionContext):
            CreateUser(appObj, userData, tenant, "adminapi/users/post", connectionContext)
            return GetUser(appObj, content["UserID"], connectionContext)
          userObj = storeConnection.executeInsideTransaction(someFn)


        except customExceptionClass as err:
          if (err.id=='TryingToCreateDuplicateUserException'):
            raise BadRequest(err.text)
          if (err.id=='InvalidUserIDException'):
            raise BadRequest(err.text)
          if (err.id=='InvalidKnownAsException'):
            raise BadRequest(err.text)
          raise Exception('InternalServerError')
        except:
          raise InternalServerError

        return userObj.getJSONRepresenation(), 201
      return appObj.objectStore.executeInsideConnectionContext(dbfn)

  @nsAdmin.route('/<string:tenant>/users/<string:userID>')
  class userInfo(Resource):

    '''Admin'''
    @nsAdmin.doc('get User')
    @nsAdmin.marshal_with(getUserModel(appObj))
    @nsAdmin.response(200, 'Success', model=getUserModel(appObj))
    @nsAdmin.response(401, 'Unauthorized')
    @nsAdmin.response(403, 'Forbidden - User dosen\'t have required role')
    @nsAdmin.response(404, 'Tenant Not Found')
    def get(self, tenant, userID):
      '''Get User information'''
      APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)
      def dbfn(storeConnection):
        userObj = GetUser(appObj, userID, storeConnection)
        if userObj is None:
          raise NotFound('User Not Found')
        return userObj.getJSONRepresenation()
      return appObj.objectStore.executeInsideConnectionContext(dbfn)

    @nsAdmin.doc('update User')
    @nsAdmin.expect(getUserModel, validate=True)
    @nsAdmin.response(200, 'User Updated')
    @nsAdmin.response(400, 'Validation Error')
    @appObj.flastRestPlusAPIObject.marshal_with(getUserModel(appObj), code=200, description='User updated')
    def put(self, tenant, userID):
      '''Update User'''
      APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)
      content_raw = request.get_json()
      content = marshal(content_raw, getUserModel(appObj))

      requiredInPayload(content, ['UserID','TenantRoles','known_as','other_data', 'ObjectVersion'])
      if userID != content['UserID']:
        raise BadRequest("Inconsistent userID")

      try:
        def someFn(connectionContext):
          return UpdateUser(
            appObj,
            content['UserID'],
            content['TenantRoles'],
            content['known_as'],
            content['other_data'],
            content['ObjectVersion'],
            connectionContext
          )
        userObj = appObj.objectStore.executeInsideTransaction(someFn)

      except customExceptionClass as err:
        if (err.id=='userDosentExistException'):
          raise BadRequest(err.text)
        if (err.id=='ShouldNotSupplySaltWhenCreatingAuthProvException'):
          raise BadRequest(err.text)
        if (err.id=='authProviderNotFoundException'):
          raise BadRequest(err.text)
        if (err.id=='cantUpdateExistingAuthProvException'):
          raise BadRequest(err.text)
        if (err.id=='InvalidAuthConfigException'):
          raise BadRequest(err.text)
        raise Exception('InternalServerError')
      except WrongObjectVersionExceptionClass as err:
        raise Conflict(err)
      except:
        raise InternalServerError

      return userObj.getJSONRepresenation()

    @nsAdmin.doc('delete User')
    @nsAdmin.response(200, 'User Deleted')
    @nsAdmin.response(400, 'Error')
    @nsAdmin.response(403, 'Forbidden - User dosen\'t have required role')
    @nsAdmin.response(409, 'Conflict')
    @appObj.flastRestPlusAPIObject.marshal_with(getUserModel(appObj), code=200, description='User Deleted')
    def delete(self, tenant, userID):
      '''Delete User'''
      decodedTokenObj = APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)
      objectVersion = None
      if objectVersionHeaderName in request.headers:
        objectVersion = request.headers.get(objectVersionHeaderName)
      if objectVersion is None:
        raise BadRequest(objectVersionHeaderName + " header missing")
      #print("Token:",decodedTokenObj.getUserID())
      #print("Passed:",userID)
      if (decodedTokenObj.getUserID() == userID):
        raise BadRequest("Can't delete logged in user")
      try:
        def someFn(connectionContext):
          return DeleteUser(appObj, userID, objectVersion, connectionContext)
        userObj = appObj.objectStore.executeInsideTransaction(someFn)

        return userObj.getJSONRepresenation()
      except customExceptionClass as err:
        if (err.id=='userDosentExistException'):
          raise BadRequest(err.text)
        raise Exception('InternalServerError')
      except WrongObjectVersionExceptionClass as err:
        raise Conflict(err)
      except:
        raise InternalServerError

  @nsAdmin.route('/<string:tenant>/persons')
  class personsInfo(Resource):

    '''Admin'''
    @nsAdmin.doc('admin')
    @nsAdmin.marshal_with(appObj.getResultModel(getPersonModel(appObj)))
    @nsAdmin.response(200, 'Success', model=appObj.getResultModel(getPersonModel(appObj)))
    @nsAdmin.response(401, 'Unauthorized')
    @nsAdmin.response(403, 'Forbidden - User dosen\'t have required role')
    @appObj.addStandardSortParams(nsAdmin)
    def get(self, tenant):
      '''Get list of persons'''
      APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)

      paginatedParamValues = getPaginatedParamValues(request)
      try:
        def someFn(connectionContext):
          def defOutput(item):
            return CreatePersonObjFromUserDict(appObj, item[0],item[1],item[2],item[3], connectionContext).getJSONRepresenation()
          return GetPaginatedPersonData(appObj, paginatedParamValues, defOutput, connectionContext)
        return appObj.objectStore.executeInsideTransaction(someFn)


      except:
        raise InternalServerError

    @nsAdmin.doc('post Person')
    @nsAdmin.expect(getCreatePersonModel(appObj), validate=True)
    @appObj.flastRestPlusAPIObject.response(400, 'Validation error')
    @appObj.flastRestPlusAPIObject.response(201, 'Created')
    @appObj.flastRestPlusAPIObject.marshal_with(getPersonModel(appObj), code=200, description='Person created', skip_none=True)
    @nsAdmin.response(403, 'Forbidden - User dosen\'t have required role')
    def post(self, tenant):
      '''Create Person'''
      APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)
      content_raw = request.get_json()
      content = marshal(content_raw, getPersonModel(appObj))

      if "guid" in content_raw:
        raise BadRequest("Can not supply guid when creating person")
      del content["guid"]
      requiredInPayload(content, [])
      try:
        def someFn(connectionContext):
          personDict = CreatePerson(appObj, connectionContext, None, 'a','b','c')
          return GetPerson(appObj, personDict["guid"], connectionContext)
        personObj = appObj.objectStore.executeInsideTransaction(someFn)

      except customExceptionClass as err:
        if (err.id=='TryingToCreateDuplicateUserException'):
          raise BadRequest(err.text)
        raise Exception('InternalServerError')
      except:
        raise InternalServerError

      return personObj.getJSONRepresenation(), 201

  @nsAdmin.route('/<string:tenant>/persons/<string:personGUID>')
  class personInfo(Resource):

    '''Admin'''
    @nsAdmin.doc('get Person')
    @nsAdmin.marshal_with(getPersonModel(appObj))
    @nsAdmin.response(200, 'Success', model=getPersonModel(appObj))
    @nsAdmin.response(401, 'Unauthorized')
    @nsAdmin.response(403, 'Forbidden - Person dosen\'t have required role')
    @nsAdmin.response(404, 'Tenant Not Found')
    def get(self, tenant, personGUID):
      '''Get Person information'''
      APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)
      def dbfn(storeConnection):
        a = GetPerson(appObj, personGUID, storeConnection)
        if a is None:
          raise NotFound('Person Not Found')
        return a.getJSONRepresenation()
      return appObj.objectStore.executeInsideConnectionContext(dbfn)

    @nsAdmin.doc('update Person')
    @nsAdmin.expect(getPersonModel, validate=True)
    @nsAdmin.response(200, 'Person Updated')
    @nsAdmin.response(400, 'Validation Error')
    @appObj.flastRestPlusAPIObject.marshal_with(getPersonModel(appObj), code=200, description='Perosn updated')
    def put(self, tenant, personGUID):
      '''Update Person'''
      APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)
      content_raw = request.get_json()
      content = marshal(content_raw, getPersonModel(appObj))

      requiredInPayload(content, ['guid', 'ObjectVersion'])
      if personGUID != content['guid']:
        raise BadRequest("Inconsistent guid")

      try:
        def someFn(connectionContext):
          return UpdatePerson(appObj, content['guid'], content['ObjectVersion'], connectionContext)
        personObj = appObj.objectStore.executeInsideTransaction(someFn)

      except customExceptionClass as err:
        if (err.id=='personDosentExistException'):
          raise BadRequest(err.text)
        raise Exception('InternalServerError')
      except WrongObjectVersionExceptionClass as err:
        raise Conflict(str(err))
      except:
        raise InternalServerError

      return personObj.getJSONRepresenation()

    @nsAdmin.doc('delete Person')
    @nsAdmin.response(200, 'Person Deleted')
    @nsAdmin.response(400, 'Error')
    @nsAdmin.response(403, 'Forbidden - Person dosen\'t have required role')
    @nsAdmin.response(409, 'Conflict')
    @appObj.flastRestPlusAPIObject.marshal_with(getPersonModel(appObj), code=200, description='Person Deleted')
    def delete(self, tenant, personGUID):
      '''Delete Person'''
      decodedTokenObj = APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)
      if personGUID == decodedTokenObj.getPersonID():
        raise BadRequest("You can't delete the logged in users person record")
      objectVersion = None
      if objectVersionHeaderName in request.headers:
        objectVersion = request.headers.get(objectVersionHeaderName)
      if objectVersion is None:
        raise BadRequest(objectVersionHeaderName + " header missing")
      try:
        def someFn(connectionContext):
          return DeletePerson(appObj, personGUID, objectVersion, connectionContext, 'a','b','c')
        personObj = appObj.objectStore.executeInsideTransaction(someFn)


        return personObj.getJSONRepresenation()
      except customExceptionClass as err:
        if (err.id=='personDosentExistException'):
          raise BadRequest(err.text)
        raise Exception('InternalServerError')
      except WrongObjectVersionExceptionClass as err:
        raise Conflict(str(err))
      except:
        raise InternalServerError

  @nsAdmin.route('/<string:tenant>/userpersonlinks/<string:userID>/<string:personGUID>')
  class userpersonlinkInfo(Resource):
    @nsAdmin.doc('post userpersonlink')
    @nsAdmin.expect(getUserPersonLinkModel(appObj), validate=True)
    @appObj.flastRestPlusAPIObject.response(400, 'Validation error')
    @appObj.flastRestPlusAPIObject.response(201, 'Created')
    @appObj.flastRestPlusAPIObject.marshal_with(getUserPersonLinkModel(appObj), code=200, description='userpersonlink created', skip_none=True)
    @nsAdmin.response(403, 'Forbidden - userpersonlink dosen\'t have required role')
    def post(self, tenant, userID, personGUID):
      '''Create userpersonlink'''
      APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)
      content_raw = request.get_json()
      content = marshal(content_raw, getUserPersonLinkModel(appObj))

      requiredInPayload(content, ["UserID", "personGUID"])
      if userID != content['UserID']:
        raise BadRequest("UserID in payload not the same as in URL")
      if personGUID != content['personGUID']:
        raise BadRequest("personGUID in payload not the same as in URL")
      def dbfn(storeConnection):
        personObj = GetPerson(appObj, content["personGUID"], storeConnection)
        if personObj is None:
          raise NotFound('Person Not Found')
        userObj = GetUser(appObj, userID, storeConnection)
        if userObj is None:
          raise NotFound('User Not Found')
        try:
          def someFn(connectionContext):
            return associateUserWithPerson(appObj, content["UserID"], content["personGUID"], connectionContext)
          storeConnection.executeInsideTransaction(someFn)

        except customExceptionClass as err:
          if (err.id=='UserAlreadyAssociatedWithThisPersonException'):
            raise BadRequest(err.text)
          raise Exception('InternalServerError')
        except:
          raise InternalServerError

        return {
          "UserID": userID,
          "personGUID": personGUID
        }, 201
      return appObj.objectStore.executeInsideConnectionContext(dbfn)

    @nsAdmin.doc('delete userpersonlink')
    @nsAdmin.response(200, 'userpersonlink Deleted')
    @nsAdmin.response(400, 'Error')
    @nsAdmin.response(403, 'Forbidden - User dosen\'t have required role')
    @nsAdmin.response(409, 'Conflict')
    @appObj.flastRestPlusAPIObject.marshal_with(getUserPersonLinkModel(appObj), code=200, description='User Person Link Deleted')
    def delete(self, tenant, userID, personGUID):
      '''Delete userpersonlink'''
      decodedTokenObj = APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)
      #No Object version needed for auths
      try:
        def someFn(connectionContext):
          RemoveUserAssociation(appObj, userID, personGUID, None, connectionContext) #Not deleting person if this is last user
          return {
            "UserID": userID,
            "personGUID": personGUID
          }
        return appObj.objectStore.executeInsideTransaction(someFn)


      except customExceptionClass as err:
        if (err.id=='personDosentExistException'):
          raise BadRequest(err.text)
        if (err.id=='userDosentExistException'):
          raise BadRequest(err.text)
        raise Exception('InternalServerError')
      except:
        raise InternalServerError

  @nsAdmin.route('/<string:tenant>/auths')
  class authsInfo(Resource):

    @nsAdmin.doc('post Auth')
    @nsAdmin.expect(getCreateAuthModel(appObj), validate=True)
    @appObj.flastRestPlusAPIObject.response(400, 'Validation error')
    @appObj.flastRestPlusAPIObject.response(201, 'Created')
    @appObj.flastRestPlusAPIObject.marshal_with(getAuthModel(appObj), code=200, description='Auth created', skip_none=True)
    @nsAdmin.response(403, 'Forbidden - User dosen\'t have required role')
    def post(self, tenant):
      '''Create Auth'''
      APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)
      content_raw = request.get_json()
      content = marshal(content_raw, getCreateAuthModel(appObj))

      requiredInPayload(content, ["personGUID", "authProviderGUID", "credentialJSON", "tenantName"])
      try:

        def someFn(connectionContext):
          authData = AddAuthForUser(appObj, content["tenantName"], content["authProviderGUID"], content["personGUID"], content["credentialJSON"], connectionContext)
          resp = {
            "personGUID": authData["personGUID"],
            "tenantName": content["tenantName"],
            "authProviderGUID": authData["AuthProviderGUID"],
            "AuthUserKey": authData["AuthUserKey"]
          }
          return resp, 201
        return appObj.objectStore.executeInsideTransaction(someFn)

      except customExceptionClass as err:
        if (err.id=='tenantDosentExistException'):
          raise BadRequest(err.text)
        if (err.id=='personDosentExistException'):
          raise BadRequest(err.text)
        if (err.id=='authProviderNotFoundException'):
          raise BadRequest(err.text)
        raise Exception('InternalServerError')
      except AuthProviders.CustomAuthProviderExceptionClass as err:
        if (err.id=='InvalidAuthConfigException'):
          raise BadRequest(err.text)
        if (err.id=='MissingAuthCredentialsException'):
          raise BadRequest(err.text)
        if (err.id=='tryingToCreateDuplicateAuthException'):
          raise BadRequest(err.text)
        raise Exception('InternalServerError')
      except:
        raise InternalServerError

  @nsAdmin.route('/<string:tenant>/auths/<string:authUserKeyEncoded>')
  class authInfo(Resource):
    @nsAdmin.doc('delete auth')
    @nsAdmin.response(200, 'auth Deleted')
    @nsAdmin.response(400, 'Error')
    @nsAdmin.response(403, 'Forbidden - User dosen\'t have required role')
    @nsAdmin.response(409, 'Conflict')
    @appObj.flastRestPlusAPIObject.marshal_with(getAuthModel(appObj), code=200, description='auth Deleted')
    def delete(self, tenant, authUserKeyEncoded):
      '''Delete auth'''
      decodedTokenObj = APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)
      #No Object version needed for auths
      authUserKey = base64.b64decode(authUserKeyEncoded).decode('utf-8')
      def dbfn(storeConnection):
        authData, objVer, creationDateTime, lastUpdateDateTime = getAuthRecord(appObj, authUserKey, storeConnection)
        if authData is None:
          raise BadRequest('Bad auth')
        try:

          def someFn(connectionContext):
            deleteAuthAndUnassiciateFromPerson(appObj, authData["personGUID"], authUserKey, connectionContext)
            resp = {
              "personGUID": authData["personGUID"],
              "tenantName": authData["tenantName"],
              "authProviderGUID": authData["AuthProviderGUID"],
              "AuthUserKey": authData["AuthUserKey"]
            }
            return resp, 200
          return storeConnection.executeInsideTransaction(someFn)

        except customExceptionClass as err:
          if (err.id=='personDosentExistException'):
            raise BadRequest(err.text)
          if (err.id=='userDosentExistException'):
            raise BadRequest(err.text)
          raise Exception('InternalServerError')
        except:
          raise InternalServerError
      return appObj.objectStore.executeInsideConnectionContext(dbfn)
