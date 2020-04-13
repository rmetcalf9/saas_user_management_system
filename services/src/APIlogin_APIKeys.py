from flask import request
from flask_restplus import Resource, fields
import constants
from werkzeug.exceptions import InternalServerError, BadRequest, NotFound
import object_store_abstraction
from baseapp_for_restapi_backend_with_swagger import getPaginatedParamValues

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
    'todo': fields.String(default='', description='TODO create model')
  })
def getAPIKeyCreateResponseModel(appObj): #APIKey model with extra raw APIKey fiels
  return appObj.flastRestPlusAPIObject.model('APIKeyCreateResponseModel', {
    'todo': fields.String(default='', description='TODO create model')
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
      if restrictedRoles == []:
        restrictedRoles = None
      externalDataDict = content['externalData']
      try:
        def dbfn(storeConnection):
          return appObj.ApiKeyManager.createAPIKey(
            decodedJWTToken=decodedJWTToken,
            restrictedRoles=restrictedRoles,
            externalDataDict=externalDataDict,
            storeConnection=storeConnection
          )
        (APIKeyObj, APIKey) = appObj.objectStore.executeInsideConnectionContext(dbfn)
        return APIKeyObj.getCreateDict(APIKey=APIKey), 201

      except constants.customExceptionClass as err:
        raise Exception('InternalServerError')
      except object_store_abstraction.RepositoryValidationException as e:
        raise BadRequest(str(e))
      except BadRequest as e:
        raise e
      except:
        raise InternalServerError

