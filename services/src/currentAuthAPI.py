#currentAuth API
from flask import request
from flask_restplus import Resource, fields
import constants
from apiSharedModels import getPersonModel, getUserModel, getLoginPostDataModel, getLoginResponseModel
from tenants import ExecuteAuthOperation, GetTenant, GetAuthProvider
from werkzeug.exceptions import BadRequest
from persons import deleteAuthAndUnassiciateFromPerson
from authsCommon import getAuthRecord
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
    'currentlyUsedAuthProviderGuid': fields.String(default='DEFAULT', description='Unique identifier of AuthProvider used for this session', required=True),
    'currentlyUsedAuthKey': fields.String(default='DEFAULT', description='Unique identifier of Auth used for this session', required=True)    
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
    'result': fields.String(default='Failed', description='Should be OK')
  })

def getDeleteAuthModelRequest(appObj):
  return appObj.flastRestPlusAPIObject.model('DeleteAuthRequestModel', {
    'AuthKey': fields.String(default='DEFAULT', description='Auth key to be deleted', required=True)
  })

def getDeleteAuthModel(appObj):
  return appObj.flastRestPlusAPIObject.model('DeleteAuthModel', {
    'result': fields.String(default='DEFAULT', description='Pass', required=True)
  })

def getLinkAuthResponseModel(appObj):
  return appObj.flastRestPlusAPIObject.model('LinkAuthResponseModel', {
    'result': fields.String(default='DEFAULT', description='Pass', required=True)
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
    [constants.jwtHeaderName], 
    [constants.jwtCookieName, constants.loginCookieName]
  )

def requiredInPayload(content, fieldList):
  for a in fieldList:
    if a not in content:
      raise BadRequest(a + ' not in payload')

  
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
        'loggedInUser': decodedJWTToken.userObj.getJSONRepresenation(),
        'currentlyUsedAuthProviderGuid': decodedJWTToken._tokenData['currentlyUsedAuthProviderGuid'],
        'currentlyUsedAuthKey': decodedJWTToken._tokenData['currentlyUsedAuthKey']
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
        
      try:
        return appObj.objectStore.executeInsideTransaction(dbfn)
      except constants.customExceptionClass as excep:
        if (excep.id=='InvalidOperationException'):
          raise Exception("Invalid operation for this auth type (" + operationName + ")")
        if (excep.id=='OperationParamMissingException'):
          raise BadRequest(excep.text)
        if (excep.id=='authopException'):
          raise BadRequest(excep.text)
        raise excep

  @nsCurAuth.route('/<string:tenant>/loggedInUserAuths/link')
  class loggedInUserAuths_LINK(Resource):
    '''Link'''
    @nsCurAuth.doc('Link')
    @nsCurAuth.expect(getLoginPostDataModel(appObj), validate=True)
    @nsCurAuth.marshal_with(getLinkAuthResponseModel(appObj), skip_none=True)
    @nsCurAuth.response(200, 'Success', model=getLinkAuthResponseModel(appObj), skip_none=True)
    @nsCurAuth.response(400, 'Bad Request')
    @nsCurAuth.response(401, 'Unauthorized')
    def post(self, tenant):
      content = request.get_json()
      requiredInPayload(content, ['authProviderGUID', 'credentialJSON'])
      authProviderGUID = content['authProviderGUID']
      credentialJSON = content['credentialJSON']

      def dbfn(storeConnection):
        decodedJWTToken = verifySecurityOfAPICall(appObj, request, tenant)
        
        # must be auth provider for logged in tenant
        tenantObj = GetTenant(tenant, storeConnection, appObj=appObj)
        authProvObj = GetAuthProvider(appObj, tenant, authProviderGUID, storeConnection, tenantObj)
        if authProvObj is None:
          raise BadRequest('Invalid auth prov GUID')
        if not authProvObj.getAllowLink():
          raise BadRequest('Not allowed to link to this authProvider')
        
        linkAuthResp = decodedJWTToken.personObj.linkAuth(appObj, authProvObj, credentialJSON, storeConnection)

        return {'result': "OK"}, 200
        
      try:
        return appObj.objectStore.executeInsideTransaction(dbfn)
      except constants.notImplemented as excep:
        raise BadRequest(excep.text)
      except constants.customExceptionClass as excep:
        if (excep.id=='linkAuthFailedException'):
          raise BadRequest(excep.text)
        if (excep.id=='InvalidAuthConfigException'):
          raise BadRequest(excep.text)
        raise excep

  @nsCurAuth.route('/<string:tenant>/loggedInUserAuths/delete')
  class loggedInUserAuths_DELETE(Resource):
    @nsCurAuth.doc('post Tenant')
    @nsCurAuth.expect(getDeleteAuthModelRequest(appObj), validate=True)
    @appObj.flastRestPlusAPIObject.response(400, 'Validation error')
    @appObj.flastRestPlusAPIObject.response(200, 'Complete - Deleted')
    @appObj.flastRestPlusAPIObject.marshal_with(getDeleteAuthModel(appObj), code=200, description='Auth Deleted')
    @nsCurAuth.response(403, 'Forbidden - User dosen\'t have required role')
    def post(self, tenant):
      '''Delete Auth'''
      decodedJWTToken = verifySecurityOfAPICall(appObj, request, tenant)
      
      content = request.get_json()
      requiredInPayload(content, ['AuthKey'])
      authKey = content["AuthKey"]
      
      def someFn(storeConnection):
        authObj, objVer, creationDateTime, lastUpdateDateTime = getAuthRecord(appObj, authKey, storeConnection)
        if authObj is None:
          raise BadRequest("Auth with this key dosen't exist")
        if authObj['AuthUserKey'] == decodedJWTToken._tokenData['currentlyUsedAuthKey']:
          raise BadRequest("Can't unlinked auth used to authenticate")
        if authObj['personGUID'] != decodedJWTToken._tokenData['authedPersonGuid']:
          raise BadRequest("Can only unlink own auths")
        
        tenantNameFromAuth = authObj['tenantName']
        
        # I am not 100% sure about this check
        if tenant != tenantNameFromAuth:
          raise BadRequest("Auth to be deleted is from a different tenant")
          
        tenantObj = GetTenant(tenantNameFromAuth, storeConnection, appObj=appObj)
        authProviderDICT = tenantObj.getAuthProvider(authObj['AuthProviderGUID'])
        if authProviderDICT is None:
          raise BadRequest("Auth provider not found")
        if not authProviderDICT['AllowUnlink']:
          raise BadRequest("Auth provider dosn't allow unlinking")

        deleteAuthAndUnassiciateFromPerson(appObj, authObj['personGUID'], authObj['AuthUserKey'], storeConnection)

        return {
          'result': "OK"
        }, 200      
      return appObj.objectStore.executeInsideTransaction(someFn)
