from flask import request
from flask_restx import Resource, fields, marshal
import constants
from werkzeug.exceptions import InternalServerError, BadRequest, NotFound
import object_store_abstraction
from baseapp_for_restapi_backend_with_swagger import getPaginatedParamValues
from object_store_abstraction import RepositoryObjBaseClass
import apiSharedModels

def requiredInPayload(content, fieldList):
  for a in fieldList:
    if a not in content:
      raise BadRequest(a + ' not in payload')

#Users must have the has account role for the specified tenant
# 401 = unauthorized -> Goes back to refresh or login makes sense to retry
# 403 = forbidden -> Will not re-prompt for login dosn't make sense to retry
def verifyJWTTokenGivesUserWithAPIKeyPrivilagesAndReturnFormattedJWTToken(appObj, request, tenant):
  try:
    return appObj.apiSecurityCheck(
      request=request,
      tenant=tenant,
      requiredRoleList=[constants.DefaultHasAccountRole],
      headersToSearch=[constants.jwtHeaderName],
      cookiesToSearch=[constants.jwtCookieName, constants.loginCookieName]
    )
  except constants.invalidPersonInToken as err:
    raise Unauthorized(err.text)
  except constants.invalidUserInToken as err:
    raise Unauthorized(err.text)

def getAPIKeyCreateRequestModel(appObj):
  return appObj.flastRestPlusAPIObject.model('APIKeyCreateRequestModel', {
    'restrictedRoles': fields.List(fields.String(default=None, description='If not an empty list a subset of the users roles to be inherited by this APIKey'), required=True),
    'externalData': fields.Raw(description='Any other data supplied during apikey creation', required=True)
  })

def getAPIKeyModel(appObj):
  return appObj.flastRestPlusAPIObject.model('APIKeyModel', {
    'id': fields.String(default='DEFAULT', description='Unique identifier of APIKey'),
    'tenantName': fields.String(default='DEFAULT', description='Name of the Tenant this APIKey associated with'),
    'createdByUserID': fields.String(default='DEFAULT', description='UserGUID of user who created this ticket'),
    'restrictedRoles': fields.List(fields.String(default=None,description='If not an empty list a subset of the users roles to be inherited by this APIKey'),required=True),
    'externalData': fields.Raw(description='Any other data supplied during apikey creation', required=True),
    RepositoryObjBaseClass.getMetadataElementKey(): fields.Nested(RepositoryObjBaseClass.getMetadataModel(appObj, flaskrestplusfields=fields))
  })
def getAPIKeyCreateResponseModel(appObj): #APIKey model with extra raw APIKey fiels
  return appObj.flastRestPlusAPIObject.model('APIKeyCreateResponseModel', {
    'apikey': fields.String(default='DEFAULT', description='APIKey'),
    'apikeydata': fields.Nested(getAPIKeyModel(appObj))
  })

def registerAPI(appObj, nsLogin):

  @nsLogin.route('/<string:tenant>/apikeys')
  class APIKeysInfo(Resource):

    @nsLogin.doc('get API Keys')
    @nsLogin.marshal_with(appObj.getResultModel(getAPIKeyModel(appObj)))
    @nsLogin.response(200, 'Success', model=appObj.getResultModel(getAPIKeyModel(appObj)))
    @nsLogin.response(401, 'Unauthorized')
    @nsLogin.response(403, 'Forbidden - User dosen\'t have required role')
    @appObj.addStandardSortParams(nsLogin)
    def get(self, tenant):
      '''Get list of ticket types'''
      decodedJWTToken = verifyJWTTokenGivesUserWithAPIKeyPrivilagesAndReturnFormattedJWTToken(appObj=appObj, request=request, tenant=tenant)
      paginatedParamValues = object_store_abstraction.sanatizePaginatedParamValues(getPaginatedParamValues(request))
      try:
        def outputFunction(itemObj):
          return itemObj.getDict()
        def dbfn(storeConnection):
          return appObj.ApiKeyManager.getAPIKeyPaginatedResults(
            decodedJWTToken=decodedJWTToken,
            tenantName=tenant,
            paginatedParamValues=paginatedParamValues,
            outputFN=outputFunction,
            storeConnection=storeConnection
          )
        return appObj.objectStore.executeInsideConnectionContext(dbfn)
      except:
        raise InternalServerError

    @nsLogin.doc('create new apikey for user and tenant')
    @nsLogin.expect(getAPIKeyCreateRequestModel(appObj), validate=True)
    @appObj.flastRestPlusAPIObject.response(400, 'Validation error')
    @appObj.flastRestPlusAPIObject.response(201, 'Created')
    @appObj.flastRestPlusAPIObject.marshal_with(getAPIKeyCreateResponseModel(appObj), code=200, description='APIKey created', skip_none=True)
    @nsLogin.response(403, 'Forbidden - User dosen\'t have required role')
    def post(self, tenant):
      '''Create APIKey'''
      decodedJWTToken = verifyJWTTokenGivesUserWithAPIKeyPrivilagesAndReturnFormattedJWTToken(appObj=appObj, request=request, tenant=tenant)
      content_raw = request.get_json()
      content = marshal(content_raw, getAPIKeyCreateRequestModel(appObj))
      requiredInPayload(content, ['restrictedRoles','externalData'])
      restrictedRoles = content['restrictedRoles']
      externalDataDict = content['externalData']
      try:
        def dbfn(storeConnection):
          return appObj.ApiKeyManager.createAPIKey(
            tenant=tenant,
            decodedJWTToken=decodedJWTToken,
            restrictedRoles=restrictedRoles,
            externalDataDict=externalDataDict,
            storeConnection=storeConnection
          )
        (APIKeyObj, APIKey) = appObj.objectStore.executeInsideTransaction(dbfn)
        return APIKeyObj.getCreateDict(APIKey=APIKey), 201

      except constants.customExceptionClass as err:
        raise Exception('InternalServerError')
      except object_store_abstraction.RepositoryValidationException as e:
        raise BadRequest(str(e))
      except BadRequest as e:
        raise e
      except:
        raise InternalServerError

  @nsLogin.route('/<string:tenant>/apikeys/<string:apiKeyID>')
  class APIKeysInfo(Resource):

    '''Get API key data from id'''
    @nsLogin.doc('get apikey')
    @nsLogin.marshal_with(getAPIKeyModel(appObj))
    @nsLogin.response(200, 'Success', model=getAPIKeyModel(appObj))
    @nsLogin.response(400, 'Bad Request')
    def get(self, tenant, apiKeyID):
     '''Get apikey for login api to use'''
     def dbfn(storeConnection):
       decodedJWTToken = verifyJWTTokenGivesUserWithAPIKeyPrivilagesAndReturnFormattedJWTToken(appObj=appObj,request=request,tenant=tenant)
       try:
         return appObj.ApiKeyManager.getAPIKeyDict(
           decodedJWTToken=decodedJWTToken,
           tenant=tenant,
           apiKeyID=apiKeyID,
           storeConnection=storeConnection
         )
       except constants.customExceptionClass as err:
         raise err
       except NotFound as e:
         raise e

     return appObj.objectStore.executeInsideTransaction(dbfn)

    @nsLogin.doc('Delete APIKey')
    @appObj.flastRestPlusAPIObject.response(400, 'Validation error')
    @appObj.flastRestPlusAPIObject.marshal_with(apiSharedModels.responseModel(appObj), code=202, description='API Key deleted', skip_none=True)
    @nsLogin.response(403, 'Forbidden - User does not have required role')
    def delete(self, tenant, apiKeyID):
      ''' Delete API Key  '''
      decodedJWTToken = verifyJWTTokenGivesUserWithAPIKeyPrivilagesAndReturnFormattedJWTToken(appObj=appObj,request=request,tenant=tenant)
      if "objectversion" not in request.args:
        raise BadRequest("Must supply object version to delete")
      if request.args["objectversion"] == None:
        raise BadRequest("Must supply object version to delete - can not be blank")
      objVer = None
      if request.args["objectversion"] != 'LOOKUP':
        objVer = request.args["objectversion"]

      def dbfn(storeConnection):
        return appObj.ApiKeyManager.deleteAPIKey(decodedJWTToken=decodedJWTToken, tenant=tenant, apiKeyID=apiKeyID, ObjectVersionNumber=objVer, storeConnection=storeConnection)
      try:
        return appObj.objectStore.executeInsideTransaction(dbfn)
      except object_store_abstraction.RepositoryValidationException as err:
        return {"response": "ERROR", "message": str(err)}, 400
      except object_store_abstraction.WrongObjectVersionExceptionClass as err:
        return { "response": "ERROR", "message": str(err) }, 409 #not using standard exception as it gives html response
        #raise Conflict(err)

  @nsLogin.route('/<string:tenant>/apikeylogin')
  class APIKeysInfo(Resource):

    '''Login using API key and get JWT Token'''
    @nsLogin.doc('get apikey')
    @nsLogin.marshal_with(apiSharedModels.getLoginResponseModel(appObj))
    @nsLogin.response(200, 'Success', model=apiSharedModels.getLoginResponseModel(appObj), skip_none=True)
    @nsLogin.response(400, 'Bad Request')
    @nsLogin.response(401, 'Unauthorized')

    def get(self, tenant):
     '''Login using API key and return JWT Token'''
     authHeader = request.headers.get('Authorization')
     if authHeader is None:
       raise BadRequest(str("Missing Authorization Header"))
     if not authHeader.startswith("Bearer "):
       raise BadRequest(str("Invalid Authorization Header"))
     apiKey = authHeader[7:]

     def dbfn(storeConnection):
       try:
         return appObj.ApiKeyManager.processAPIKeyLogin(
           apiKey=apiKey,
           tenantName=tenant,
           storeConnection=storeConnection
         )
       except constants.customExceptionClass as err:
         raise err
       except NotFound as e:
         raise e
       except BadRequest as e:
         raise e

     return appObj.objectStore.executeInsideTransaction(dbfn)
