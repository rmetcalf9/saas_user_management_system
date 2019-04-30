#currentAuth API
from flask import request
from flask_restplus import Resource, fields
from constants import jwtHeaderName, jwtCookieName, loginCookieName
from apiSharedModels import getPersonModel, getUserModel
from persons import GetPerson
from userPersonCommon import GetUser
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
      def someFn(connectionContext):
        return GetPerson(appObj, decodedJWTToken.getPersonID(), connectionContext), GetUser(appObj, decodedJWTToken.getUserID(), connectionContext)
      personObj, userObj = appObj.objectStore.executeInsideTransaction(someFn)
      
      print()
      return {
        'loggedInPerson': personObj.getJSONRepresenation(),
        'loggedInUser': userObj.getJSONRepresenation()
      }
