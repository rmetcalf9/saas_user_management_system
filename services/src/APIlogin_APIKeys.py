from flask import request
from flask_restplus import Resource, fields
import constants
from werkzeug.exceptions import InternalServerError, BadRequest, NotFound
import object_store_abstraction
from baseapp_for_restapi_backend_with_swagger import getPaginatedParamValues
from object_store_abstraction import RepositoryObjBaseClass

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
  class APIKeyInfo(Resource):

    @nsLogin.doc('create new apikey for user and tenant')
    @nsLogin.expect(getAPIKeyCreateRequestModel(appObj), validate=True)
    @appObj.flastRestPlusAPIObject.response(400, 'Validation error')
    @appObj.flastRestPlusAPIObject.response(201, 'Created')
    @appObj.flastRestPlusAPIObject.marshal_with(getAPIKeyCreateResponseModel(appObj), code=200, description='APIKey created', skip_none=True)
    @nsLogin.response(403, 'Forbidden - User dosen\'t have required role')
    def post(self, tenant):
      '''Create APIKey'''
      decodedJWTToken = verifyJWTTokenGivesUserWithAPIKeyPrivilagesAndReturnFormattedJWTToken(appObj=appObj, request=request, tenant=tenant)
      content = request.get_json()
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

