#Admin API
from flask import request
from flask_restplus import Resource, fields
from werkzeug.exceptions import Unauthorized, Forbidden, BadRequest, InternalServerError, NotFound, Conflict
from apiSecurity import verifyAPIAccessUserLoginRequired
from constants import masterTenantDefaultSystemAdminRole, masterTenantName, jwtHeaderName, jwtCookieName, loginCookieName, customExceptionClass, ShouldNotSupplySaltWhenCreatingAuthProvException, objectVersionHeaderName
from apiSharedModels import getTenantModel, getUserModel
from urllib.parse import unquote
import json
from jwt.exceptions import InvalidSignatureError, ExpiredSignatureError
from tenants import CreateTenant, UpdateTenant, DeleteTenant, GetTenant
from userPersonCommon import GetUser, CreateUserObjFromUserDict, RemoveUserAssociation
from users import GetPaginatedUserData, UpdateUser, DeleteUser, CreateUser, associateUserWithPerson
from persons import GetPaginatedPersonData, CreatePerson, GetPerson, UpdatePerson, DeletePerson, CreatePersonObjFromUserDict
from tenantObj import tenantClass
from userObj import userClass
from personObj import personClass
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
  
def getCreateUserModel(appObj):
  return appObj.flastRestPlusAPIObject.model('CreateUserInfo', {
    'UserID': fields.String(default='DEFAULT', description='Unique identifier of User'),
    'known_as': fields.String(description='User friendly identifier for username'),
    'mainTenant': fields.String(description='If set then a hasaccount role is setup for this tenant'),
  })

def getCreatePersonModel(appObj):
  return appObj.flastRestPlusAPIObject.model('CreatePersonInfo', {
  })

def getPersonModel(appObj):
  return appObj.flastRestPlusAPIObject.model('PersonInfo', {
    'guid': fields.String(default='DEFAULT', description='Unique identifier of Person'),
    'associatedUsers': fields.List(fields.Nested(getUserModel(appObj))),
    'ObjectVersion': fields.String(default='DEFAULT', description='Obect version required to sucessfully preform updates'),
    'creationDateTime': fields.DateTime(dt_format=u'iso8601', description='Datetime user was created'),
    'lastUpdateDateTime': fields.DateTime(dt_format=u'iso8601', description='Datetime user was lastupdated')
  })

def getUserPersonLinkModel(appObj):
  return appObj.flastRestPlusAPIObject.model('UserPersonLinkInfo', {
    'UserID': fields.String(default='DEFAULT', description='Unique identifier of User'),
    'personGUID': fields.String(default='DEFAULT', description='Unique identifier of Person')
  })

  
def requiredInPayload(content, fieldList):
  for a in fieldList:
    if a not in content:
      raise BadRequest(a + ' not in payload')

def verifySecurityOfAdminAPICall(appObj, request, tenant):
  #Admin api can only be called from masterTenant
  if tenant != masterTenantName:
    raise Unauthorized("Supplied tenant is not the master tenant")
  
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
  forbidden = False
  try:
    (verified, decodedTokenObj, forbidden) = verifyAPIAccessUserLoginRequired(appObj, tenant, jwtToken, [masterTenantDefaultSystemAdminRole])
  except InvalidSignatureError:
    raise Unauthorized("InvalidSignatureError")
  except ExpiredSignatureError:
    raise Unauthorized("ExpiredSignatureError")
  except Exception:
    raise Unauthorized("Problem with token")
    
  if (forbidden):
    raise Forbidden("Forbidden")
  if not verified:
    raise Unauthorized("not verified")
  return decodedTokenObj
  
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
        return appObj.objectStore.getPaginatedResult(appObj, "tenants", appObj.getPaginatedParamValues(request), request, outputFN)
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
      verifySecurityOfAdminAPICall(appObj, request, tenant)
      content = request.get_json()
      requiredInPayload(content, ['Name','Description','AllowUserCreation'])
      if "AuthProviders" in content:
        if len(content["AuthProviders"]) != 0:
          raise BadRequest("Not possible to create a Tenant with AuthProviders ")
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
    @appObj.flastRestPlusAPIObject.marshal_with(getTenantModel(appObj), code=200, description='Tenant Deleted')
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
      verifySecurityOfAdminAPICall(appObj, request, tenant)
      def defOutput(item):
        return CreateUserObjFromUserDict(appObj, item[0],item[1],item[2],item[3]).getJSONRepresenation()

      try:
        outputFN = defOutput
        return GetPaginatedUserData(appObj, request, outputFN)
      except Exception as e:
        print(e)
        print(str(e.args))
        print(e.args)
        raise InternalServerError   

    @nsAdmin.doc('post User')
    @nsAdmin.expect(getCreateUserModel(appObj), validate=True)
    @appObj.flastRestPlusAPIObject.response(400, 'Validation error')
    @appObj.flastRestPlusAPIObject.response(201, 'Created')
    @appObj.flastRestPlusAPIObject.marshal_with(getUserModel(appObj), code=200, description='User created', skip_none=True)
    @nsAdmin.response(403, 'Forbidden - User dosen\'t have required role')
    def post(self, tenant):
      '''Create User'''
      verifySecurityOfAdminAPICall(appObj, request, tenant)
      content = request.get_json()
      requiredInPayload(content, ['UserID','known_as'])
      userData = {
        "user_unique_identifier": content["UserID"],
        "known_as": content["known_as"]
      }
      tenant = None
      if "mainTenant" in content:
        if content["mainTenant"] != "":
          tenant = content["mainTenant"]
          tenantObj = GetTenant(appObj, tenant)
          if tenantObj is None:
            raise BadRequest("Invalid tenant name")
      try:
        CreateUser(appObj, userData, tenant, "adminapi/users/post")
        userObj = GetUser(appObj, content["UserID"])
      except customExceptionClass as err:
        if (err.id=='TryingToCreateDuplicateUserException'):
          raise BadRequest(err.text)
        raise Exception('InternalServerError')
      except:
        raise InternalServerError
      
      return userObj.getJSONRepresenation(), 201


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
      verifySecurityOfAdminAPICall(appObj, request, tenant)
      userObj = GetUser(appObj, userID)
      if userObj is None:
        raise NotFound('User Not Found')
      return userObj.getJSONRepresenation()

    @nsAdmin.doc('update User')
    @nsAdmin.expect(getUserModel, validate=True)
    @nsAdmin.response(200, 'User Updated')
    @nsAdmin.response(400, 'Validation Error')
    @appObj.flastRestPlusAPIObject.marshal_with(getUserModel(appObj), code=200, description='User updated')
    def put(self, tenant, userID):
      '''Update User'''
      verifySecurityOfAdminAPICall(appObj, request, tenant)
      content = request.get_json()
      requiredInPayload(content, ['UserID','TenantRoles','known_as','other_data', 'ObjectVersion'])
      if userID != content['UserID']:
        raise BadRequest("Inconsistent userID")

      try:
        userObj = UpdateUser(appObj, content['UserID'], content['TenantRoles'], content['known_as'],  content['other_data'], content['ObjectVersion'])
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
      decodedTokenObj = verifySecurityOfAdminAPICall(appObj, request, tenant)
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
        userObj = DeleteUser(appObj, userID, objectVersion)
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
      verifySecurityOfAdminAPICall(appObj, request, tenant)
      def defOutput(item):
        return CreatePersonObjFromUserDict(appObj, item[0],item[1],item[2],item[3]).getJSONRepresenation()

      try:
        outputFN = defOutput
        return GetPaginatedPersonData(appObj, request, outputFN)
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
      verifySecurityOfAdminAPICall(appObj, request, tenant)
      content = request.get_json()
      if "guid" in content:
        raise BadRequest("Can not supply guid when creating person")
      requiredInPayload(content, [])
      try:
        personDict = CreatePerson(appObj)
        personObj = GetPerson(appObj, personDict["guid"])
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
      verifySecurityOfAdminAPICall(appObj, request, tenant)
      a = GetPerson(appObj, personGUID)
      if a is None:
        raise NotFound('Person Not Found')
      return a.getJSONRepresenation()

    @nsAdmin.doc('update Person')
    @nsAdmin.expect(getPersonModel, validate=True)
    @nsAdmin.response(200, 'Person Updated')
    @nsAdmin.response(400, 'Validation Error')
    @appObj.flastRestPlusAPIObject.marshal_with(getPersonModel(appObj), code=200, description='Perosn updated')
    def put(self, tenant, personGUID):
      '''Update Person'''
      verifySecurityOfAdminAPICall(appObj, request, tenant)
      content = request.get_json()
      requiredInPayload(content, ['guid', 'ObjectVersion'])
      if personGUID != content['guid']:
        raise BadRequest("Inconsistent guid")

      try:
        personObj = UpdatePerson(appObj, content['guid'], content['ObjectVersion'])
      except customExceptionClass as err:
        if (err.id=='personDosentExistException'):
          raise BadRequest(err.text)
        raise Exception('InternalServerError')
      except WrongObjectVersionExceptionClass as err:
        raise Conflict(err)
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
      decodedTokenObj = verifySecurityOfAdminAPICall(appObj, request, tenant)
      if personGUID == decodedTokenObj.getPersonID():
        raise BadRequest("You can't delete the logged in users person record")
      objectVersion = None
      if objectVersionHeaderName in request.headers:
        objectVersion = request.headers.get(objectVersionHeaderName)
      if objectVersion is None:
        raise BadRequest(objectVersionHeaderName + " header missing")
      try:
        personObj = DeletePerson(appObj, personGUID, objectVersion)
        return personObj.getJSONRepresenation()
      except customExceptionClass as err:
        if (err.id=='personDosentExistException'):
          raise BadRequest(err.text)
        raise Exception('InternalServerError')
      except WrongObjectVersionExceptionClass as err:
        raise Conflict(err)
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
      verifySecurityOfAdminAPICall(appObj, request, tenant)
      content = request.get_json()
      requiredInPayload(content, ["UserID", "personGUID"])
      if userID != content['UserID']:
        raise BadRequest("UserID in payload not the same as in URL")
      if personGUID != content['personGUID']:
        raise BadRequest("personGUID in payload not the same as in URL")
      personObj = GetPerson(appObj, content["personGUID"])
      if personObj is None:
        raise NotFound('Person Not Found')
      userObj = GetUser(appObj, userID)
      if userObj is None:
        raise NotFound('User Not Found')
      try:
        associateUserWithPerson(appObj, content["UserID"], content["personGUID"])
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

    @nsAdmin.doc('delete userpersonlink')
    @nsAdmin.response(200, 'userpersonlink Deleted')
    @nsAdmin.response(400, 'Error')
    @nsAdmin.response(403, 'Forbidden - User dosen\'t have required role')
    @nsAdmin.response(409, 'Conflict')
    @appObj.flastRestPlusAPIObject.marshal_with(getUserPersonLinkModel(appObj), code=200, description='User Person Link Deleted')
    def delete(self, tenant, userID, personGUID):
      '''Delete userpersonlink'''
      decodedTokenObj = verifySecurityOfAdminAPICall(appObj, request, tenant)
      #No Object version needed for auths
      try:
        RemoveUserAssociation(appObj, userID, personGUID, None) #Not deleting person if this is last user
        return {
          "UserID": userID,
          "personGUID": personGUID
        }
      except customExceptionClass as err:
        if (err.id=='personDosentExistException'):
          raise BadRequest(err.text)
        if (err.id=='userDosentExistException'):
          raise BadRequest(err.text)
        raise Exception('InternalServerError')
      except:
        raise InternalServerError
      