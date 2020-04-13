from flask import request
from flask_restplus import Resource, fields
import constants
from werkzeug.exceptions import InternalServerError, BadRequest, NotFound
import object_store_abstraction
from baseapp_for_restapi_backend_with_swagger import getPaginatedParamValues

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
    'todo': fields.String(default='', description='TODO create model')
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
      verifyJWTTokenGivesUserWithAPIKeyPrivilagesAndReturnFormattedJWTToken(appObj=appObj, request=request, tenant=tenant)
      content = request.get_json()
      #requiredInPayload(content, ['Name','Description','AllowUserCreation'])
      try:
        raise Exception("Not Implemented")
      except constants.customExceptionClass as err:
        raise Exception('InternalServerError')
      except object_store_abstraction.RepositoryValidationException as e:
        raise BadRequest(str(e))
      except BadRequest as e:
        raise e
      except:
        raise InternalServerError

      #Use getCreateDict as this returns the API key as well as the object
      ##return APIKeyObj.getCreateDict(APIKey=apiKey), 201

