#Admin API
from flask import request
from flask_restplus import Resource, fields
from werkzeug.exceptions import Unauthorized, Forbidden, BadRequest, InternalServerError, NotFound, Conflict
from apiSecurity import verifyAPIAccessUserLoginRequired
from constants import masterTenantDefaultSystemAdminRole, masterTenantName, jwtHeaderName, jwtCookieName, loginCookieName, customExceptionClass, ShouldNotSupplySaltWhenCreatingAuthProvException, objectVersionHeaderName
from apiSharedModels import getTenantModel
from urllib.parse import unquote
import json
from jwt.exceptions import InvalidSignatureError, ExpiredSignatureError
from tenants import CreateTenant, UpdateTenant, DeleteTenant, GetTenant
from users import GetPaginatedUserData
from tenantObj import tenantClass
from objectStores_base import WrongObjectVersionExceptionClass
import copy

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
    'AllowUserCreation': fields.Boolean(default=False,description='Allow unknown logins to create new users. (Must be set to true at this level AND AuthPRovider level to work)')
  })

def getUserModel(appObj):
  TenantRoleModel = appObj.flastRestPlusAPIObject.model('TenantRoleModel', {
    'TenantName': fields.String(default='DEFAULT', description='Tenant Name'),
    'ThisTenantRoles': fields.List(fields.String(description='Role the user has been assigned for this tenant')),
  })

  return appObj.flastRestPlusAPIObject.model('UserInfo', {
    'UserID': fields.String(default='DEFAULT', description='Unique identifier of User'),
    'known_as': fields.String(description='User friendly identifier for username'),
    'TenantRoles': fields.List(fields.Nested(TenantRoleModel)),
    'other_data': fields.Raw(description='Any other data supplied by auth provider', required=True)
  })

  
def requiredInPayload(content, fieldList):
  for a in fieldList:
    if a not in content:
      raise BadRequest(a + ' not in payload')

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
    raise Unauthorized("No JWT Token in header or cookie")
  
  try:
    (verified, decodedToken, forbidden) = verifyAPIAccessUserLoginRequired(appObj, tenant, jwtToken, [masterTenantDefaultSystemAdminRole])
    if (forbidden):
      raise Forbidden()
  except InvalidSignatureError:
    raise Unauthorized("InvalidSignatureError")
  except ExpiredSignatureError:
    raise Unauthorized("ExpiredSignatureError")
  if not verified:
    raise Unauthorized("not verified")
  
def registerAPI(appObj):
  nsAdmin = appObj.flastRestPlusAPIObject.namespace('authed/admin', description='API for accessing admin functions.')

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
      verifySecurityOfAdminAPICall(appObj, request, tenant)
      def defOutput(item):
        return tenantClass(item[0],item[1]).getJSONRepresenation()

      try:
        outputFN = defOutput
        filterFN = None
        return appObj.objectStore.getPaginatedResult(appObj, "tenants", appObj.getPaginatedParamValues(request), request, outputFN, filterFN)
      except:
        raise InternalServerError   

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

    @nsAdmin.doc('post Tenant')
    @nsAdmin.expect(getCreateTenantModel(appObj), validate=True)
    @appObj.flastRestPlusAPIObject.response(400, 'Validation error')
    @appObj.flastRestPlusAPIObject.response(201, 'Created')
    @appObj.flastRestPlusAPIObject.marshal_with(getTenantModel(appObj), code=200, description='Tenant created', skip_none=True)
    @nsAdmin.response(403, 'Forbidden - User dosen\'t have required role')
    def post(self, tenant):
      '''Create Tenant'''
      verifySecurityOfAdminAPICall(appObj, request, tenant)
      content = request.get_json()
      requiredInPayload(content, ['Name','Description','AllowUserCreation'])
      try:
        tenantObj = CreateTenant(appObj, content['Name'], content['Description'], content['AllowUserCreation'])
      except customExceptionClass as err:
        if (err.id=='tenantAlreadtExistsException'):
          raise BadRequest(err.text)
        raise Exception('InternalServerError')
      except:
        raise InternalServerError
      
      return tenantObj.getJSONRepresenation(), 201

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
      verifySecurityOfAdminAPICall(appObj, request, tenant)
      a = GetTenant(appObj, tenantName)
      if a is None:
        raise NotFound('Tenant Not Found')
      return a.getJSONRepresenation()

    @nsAdmin.doc('update Tenant')
    @nsAdmin.expect(getTenantModel, validate=True)
    @nsAdmin.response(200, 'Tenant Updated')
    @nsAdmin.response(400, 'Validation Error')
    @appObj.flastRestPlusAPIObject.marshal_with(getTenantModel(appObj), code=200, description='Tenant updated')
    def put(self, tenant, tenantName):
      '''Update Tenant'''
      verifySecurityOfAdminAPICall(appObj, request, tenant)
      content = request.get_json()
      requiredInPayload(content, ['Name','Description','AllowUserCreation','AuthProviders','ObjectVersion'])

      try:
        content = updateContentConvertingInputStringsToDictsWhereRequired(content)
        tenantObj = UpdateTenant(appObj, content['Name'], content['Description'], content['AllowUserCreation'],  content['AuthProviders'], content['ObjectVersion'])
      except customExceptionClass as err:
        if (err.id=='tenantDosentExistException'):
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
      
      return tenantObj.getJSONRepresenation()

    @nsAdmin.doc('delete Tenant')
    @nsAdmin.response(200, 'Tenant Deleted')
    @nsAdmin.response(400, 'Error')
    @nsAdmin.response(403, 'Forbidden - User dosen\'t have required role')
    @nsAdmin.response(409, 'Conflict')
    @appObj.flastRestPlusAPIObject.marshal_with(getTenantModel(appObj), code=200, description='Tenant updated')
    def delete(self, tenant, tenantName):
      '''Delete Tenant'''
      verifySecurityOfAdminAPICall(appObj, request, tenant)
      objectVersion = None
      if objectVersionHeaderName in request.headers:
        objectVersion = request.headers.get(objectVersionHeaderName)
      if objectVersion is None:
        raise BadRequest(objectVersionHeaderName + " header missing")
      try:
        tenantObj = DeleteTenant(appObj, tenantName, objectVersion)
        return tenantObj.getJSONRepresenation()
      except customExceptionClass as err:
        if (err.id=='tenantDosentExistException'):
          raise BadRequest(err.text)
        if (err.id=='cantDeleteMasterTenantException'):
          raise BadRequest(err.text)
        raise Exception('InternalServerError')
      except WrongObjectVersionExceptionClass as err:
        raise Conflict(err)
      except:
        raise InternalServerError        

  @nsAdmin.route('/<string:tenant>/users')
  class userssInfo(Resource):
  
    '''Admin'''
    @nsAdmin.doc('admin')
    @nsAdmin.marshal_with(appObj.getResultModel(getUserModel(appObj)))
    @nsAdmin.response(200, 'Success', model=appObj.getResultModel(getUserModel(appObj)))
    @nsAdmin.response(401, 'Unauthorized')
    @nsAdmin.response(403, 'Forbidden - User dosen\'t have required role')
    @appObj.addStandardSortParams(nsAdmin)
    def get(self, tenant):
      '''Get list of users'''
      verifySecurityOfAdminAPICall(appObj, request, tenant)
      def defOutput(item):
        returnValue = copy.deepcopy(item[0])
        tenantRolesObj = []
        for a in returnValue['TenantRoles']:
          tenantRolesObj.append({
            "TenantName": a,
            "ThisTenantRoles": returnValue['TenantRoles'][a]
          })
          returnValue["TenantRoles"] = tenantRolesObj
        return returnValue
        ##return tenantClass(item[0],item[1]).getJSONRepresenation()

      try:
        outputFN = defOutput
        filterFN = None
        return GetPaginatedUserData(appObj, request, outputFN, filterFN)
      except Exception as e:
        print(e)
        print(str(e.args))
        print(e.args)
        raise InternalServerError   
