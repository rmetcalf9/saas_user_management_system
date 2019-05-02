#currentAuth API
from flask import request
from flask_restplus import Resource, fields
from constants import jwtHeaderName, jwtCookieName, loginCookieName
from apiSharedModels import getPersonModel, getUserModel
from tenants import ExecuteAuthOperation
'''
The currentAuth API includes functionality availiable for authed users

Security:
 - they do not need an has account role for the tenant
'''

def getCurrentAuthModel(appObj):
  return appObj.flastRestPlusAPIObject.model('Current Auth', {
    #'XX': fields.String(default='DEFAULT', description='Unique identifier of Auth'),
    'loggedInPerson': fields.Nested(getPersonModel(appObj)),
    'loggedInUser': fields.Nested(getUserModel(appObj)),
  })

def getExecuteAuthOperationModel(appObj):
  return appObj.flastRestPlusAPIObject.model('Execute Auth Operation Request', {
    'authProviderGUID': fields.String(default='DEFAULT', description='Unique identifier of AuthProvider for operation', required=True),
    'credentialJSON': fields.Raw(description='JSON structure required depends on the Auth Provider type', required=True),
    'operationName': fields.String(description='Name of operation to preform', required=True),
    'operationData': fields.Raw(description='JSON structure required depends on the Auth Provider type and operation', required=True),
  })
def getExecuteAuthOperationResponseModel(appObj):
  return appObj.flastRestPlusAPIObject.model('Execute Auth Operation Response', {
    'Result': fields.String(default='Failed', description='Should be OK')
  })


def requiredInPayload(content, fieldList):
  for a in fieldList:
    if a not in content:
      raise BadRequest(a + ' not in payload')


#401 = unauthorized -> Goes back to refresh or login makes sense to retry
#403 = forbidden -> Will not re-prompt for login dosn't make sense to retry
def verifySecurityOfAPICall(appObj, request, tenant):
  requiredRoles = []
  
  return appObj.apiSecurityCheck(
    request, 
    tenant, 
    requiredRoles, 
    [jwtHeaderName], 
    [jwtCookieName, loginCookieName]
  )

  
def registerAPI(appObj):
  nsCurAuth = appObj.flastRestPlusAPIObject.namespace('authed/currentAuth', description='API for accessing functions for the currently authed user/person.')

  @nsCurAuth.route('/<string:tenant>/currentAuthInfo')
  class currentAuthInfo(Resource):
    '''Current Auth Info'''
    @nsCurAuth.doc('currentAuthInfo')
    @nsCurAuth.marshal_with(getCurrentAuthModel(appObj))
    @nsCurAuth.response(200, 'Success', model=getCurrentAuthModel(appObj))
    @nsCurAuth.response(401, 'Unauthorized')
    @nsCurAuth.response(403, 'Forbidden - User dosen\'t have required role')
    @appObj.addStandardSortParams(nsCurAuth)
    def get(self, tenant):
      '''Get list of tenants'''
      decodedJWTToken = verifySecurityOfAPICall(appObj, request, tenant)

      return {
        'loggedInPerson': decodedJWTToken.personObj.getJSONRepresenation(),
        'loggedInUser': decodedJWTToken.userObj.getJSONRepresenation()
      }

    @nsCurAuth.doc('post Auth Operation')
    @nsCurAuth.expect(getExecuteAuthOperationModel(appObj), validate=True)
    @appObj.flastRestPlusAPIObject.response(400, 'Validation error')
    @appObj.flastRestPlusAPIObject.marshal_with(getExecuteAuthOperationResponseModel(appObj), code=200, description='Operation Complete', skip_none=True)
    @nsCurAuth.response(403, 'Forbidden - User dosen\'t have required role')
    def post(self, tenant):
      '''Execute Auth Operation'''
      decodedJWTToken = verifySecurityOfAPICall(appObj, request, tenant)

      content = request.get_json()
      requiredInPayload(content, ['authProviderGUID', 'credentialJSON','operationData','operationName'])

      authProvGUID = request.get_json()['authProviderGUID']
      credentialDICT = request.get_json()['credentialJSON']
      operationDICT = request.get_json()['operationData']
      operationName = request.get_json()['operationName']

      def dbfn(storeConnection):
        ExecuteAuthOperation(appObj, credentialDICT, storeConnection, operationName, operationDICT, tenant, authProvGUID)
        return {
          'Result': 'OK'
        }, 200
      return appObj.objectStore.executeInsideTransaction(dbfn)

