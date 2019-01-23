#Admin API
from flask import request
from flask_restplus import Resource, fields
from werkzeug.exceptions import Unauthorized
from apiSecurity import verifyAPIAccessUserLoginRequired
from constants import masterTenantDefaultSystemAdminRole, masterTenantName, jwtHeaderName, jwtCookieName, loginCookieName
from apiSharedModels import getTenantModel
from urllib.parse import unquote
import json

def verifySecurityOfAdminAPICall(appObj, request, tenant):
  #Admin api can only be called from masterTenant
  if tenant != masterTenantName:
    raise Unauthorized()
  
  jwtToken = None
  if jwtHeaderName in request.headers:
    jwtToken = request.headers.get(jwtHeaderName)
  elif jwtCookieName in request.cookies:
    jwtToken = request.cookies.get(jwtCookieName)
  elif loginCookieName in request.cookies:
    a = request.cookies.get(loginCookieName)
    a = unquote(a)
    a = json.loads(a)
    if 'jwtData' in a.keys():
      if 'JWTToken' in a['jwtData']:
        jwtToken = a['jwtData']['JWTToken']
  if jwtToken is None:
    raise Unauthorized()

  (verified, decodedToken) = verifyAPIAccessUserLoginRequired(appObj, tenant, jwtToken, [masterTenantDefaultSystemAdminRole])
  if not verified:
    raise Unauthorized()
  
def getPaginatedParamValues(request):
  pagesizemax = 500
  offset = request.args.get('offset')
  if offset is None:
    offset = 0
  else:
    offset = int(offset)
  pagesize = request.args.get('pagesize')
  if pagesize is None:
    pagesize = 100
  else:
    pagesize = int(pagesize)
  if pagesize > pagesizemax:
    pagesize = pagesizemax
  
  sort = request.args.get('sort')
  query = request.args.get('query')
  return {
    'offset': offset,
    'pagesize': pagesize,
    'query': query,
    'sort': sort,
  }

def registerAPI(appObj):
  nsAdmin = appObj.flastRestPlusAPIObject.namespace('authed/admin', description='API for accessing admin functions.')

  @nsAdmin.route('/<string:tenant>/tenants')
  class tenantInfo(Resource):
  
    '''Admin'''
    @nsAdmin.doc('admin')
    #@nsJobs.marshal_with(appObj.getResultModel(getTenantModel(appObj)))
    #@nsAdmin.response(200, 'Success', model=appObj.getResultModel(getTenantModel(appObj)))
    @nsAdmin.response(401, 'Unauthorized')
    @appObj.addStandardSortParams(nsAdmin)
    def get(self, tenant):
      '''Get list of tenants'''
      verifySecurityOfAdminAPICall(appObj, request, tenant)
      def defOutput(item):
        return item

      outputFN = defOutput
      filterFN = None
      return appObj.objectStore.getPaginatedResult(appObj, "tenants", getPaginatedParamValues(request), request, outputFN, filterFN)

#      def output(item):
#        return item
#        #return appObj.appData['jobsData'].jobs[item]._caculatedDict(appObj)
#      def filter(item, whereClauseText): #if multiple separated by spaces each is passed individually and anded together
#        #if whereClauseText.find('=') == -1:
#        #  if appObj.appData['jobsData'].jobs[item].name.upper().find(whereClauseText) != -1:
#        #    return True
#        #  if appObj.appData['jobsData'].jobs[item].command.upper().find(whereClauseText) != -1:
#        #    return True
#        #  return False
#        ##only supports a single search param
#        #sp = whereClauseText.split("=")
#        #if sp[0]=="PINNED":
#        #  if sp[1]=="TRUE":
#        #     return appObj.appData['jobsData'].jobs[item].pinned
#        #  if sp[1]=="FALSE":
#        #     return not appObj.appData['jobsData'].jobs[item].pinned
#        #  return False
#        #return False
#        return True
#      return appObj.getPaginatedResult(
#        [], #appObj.appData['jobsData'].jobs_name_lookup,
#        output,
#        request,
#        filter
#      )


