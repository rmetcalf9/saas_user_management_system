#Admin API
from flask import request
from flask_restplus import Resource, fields
from werkzeug.exceptions import Unauthorized, Forbidden, BadRequest, InternalServerError, NotFound, Conflict
from constants import masterTenantDefaultSystemAdminRole, masterTenantName, jwtHeaderName, jwtCookieName, loginCookieName, customExceptionClass, ShouldNotSupplySaltWhenCreatingAuthProvException, objectVersionHeaderName, DefaultHasAccountRole
from apiSharedModels import getTenantModel, getUserModel
from urllib.parse import unquote
import json
from tenants import CreateTenant, UpdateTenant, DeleteTenant, GetTenant, AddAuthForUser
from authsCommon import getAuthRecord
from userPersonCommon import GetUser, CreateUserObjFromUserDict, RemoveUserAssociation
from users import GetPaginatedUserData, UpdateUser, DeleteUser, CreateUser, associateUserWithPerson
from persons import GetPaginatedPersonData, CreatePerson, GetPerson, UpdatePerson, DeletePerson, CreatePersonObjFromUserDict, deleteAuthAndUnassiciateFromPerson
from tenantObj import tenantClass
from objectStores_base import WrongObjectVersionExceptionClass
import copy
import base64
from baseapp_for_restapi_backend_with_swagger import getPaginatedParamValues


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
  personAuthsModel = appObj.flastRestPlusAPIObject.model('PersonAuthsInfo', {
    'AuthUserKey': fields.String(default='DEFAULT', description='Unique identifier of Auth'),
    'AuthProviderType': fields.String(default='DEFAULT', description='Type of AuthProvider for this Auth'),
    'AuthProviderGUID': fields.String(default='DEFAULT', description='Unique identifier of AuthProvider for this Auth'),
    'tenantName': fields.String(default='DEFAULT', description='Name of the Tenant this auth is associated with')
  })
  return appObj.flastRestPlusAPIObject.model('PersonInfo', {
    'guid': fields.String(default='DEFAULT', description='Unique identifier of Person'),
    'associatedUsers': fields.List(fields.Nested(getUserModel(appObj))),
    'personAuths': fields.List(fields.Nested(personAuthsModel)),
    'ObjectVersion': fields.String(default='DEFAULT', description='Obect version required to sucessfully preform updates'),
    'creationDateTime': fields.DateTime(dt_format=u'iso8601', description='Datetime user was created'),
    'lastUpdateDateTime': fields.DateTime(dt_format=u'iso8601', description='Datetime user was lastupdated')
  })

def getUserPersonLinkModel(appObj):
  return appObj.flastRestPlusAPIObject.model('UserPersonLinkInfo', {
    'UserID': fields.String(default='DEFAULT', description='Unique identifier of User'),
    'personGUID': fields.String(default='DEFAULT', description='Unique identifier of Person')
  })

def getCreateAuthModel(appObj):
  return appObj.flastRestPlusAPIObject.model('CreateAuthInfo', {
    'personGUID': fields.String(default='DEFAULT', description='Unique identifier of Person', required=True),
    'tenantName': fields.String(description='Name of Tenant'),
    'authProviderGUID': fields.String(default='DEFAULT', description='Unique identifier of Person', required=True),
    'credentialJSON': fields.Raw(description='JSON structure required depends on the Auth Provider type', required=True),
  })

def getAuthModel(appObj):
  return appObj.flastRestPlusAPIObject.model('AuthInfo', {
    'personGUID': fields.String(default='DEFAULT', description='Unique identifier of Person', required=True),
    'tenantName': fields.String(description='Name of Tenant'),
    'authProviderGUID': fields.String(default='DEFAULT', description='Unique identifier of Person', required=True),
    'AuthUserKey': fields.String(default='DEFAULT', description='Unique identifier of Auth'),
  })
  
def requiredInPayload(content, fieldList):
  for a in fieldList:
    if a not in content:
      raise BadRequest(a + ' not in payload')

#401 = unauthorized -> Goes back to refresh or login makes sense to retry
#403 = forbidden -> Will not re-prompt for login dosn't make sense to retry
def verifySecurityOfAdminAPICall(appObj, request, tenant):
  #Admin api can only be called from masterTenant
  if tenant != masterTenantName:
    raise Unauthorized("Supplied tenant is not the master tenant")
  return appObj.apiSecurityCheck(
    request, 
    tenant, 
    [DefaultHasAccountRole, masterTenantDefaultSystemAdminRole], 
    [jwtHeaderName], 
    [jwtCookieName, loginCookieName]
  )

  
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
        def dbfn(storeConnection):
          outputFN = defOutput
          return storeConnection.getPaginatedResult("tenants", getPaginatedParamValues(request), outputFN)
        return appObj.objectStore.executeInsideConnectionContext(dbfn)
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
        def someFn(connectionContext):
          return CreateTenant(appObj, content['Name'], content['Description'], content['AllowUserCreation'], connectionContext, 'a','b','c')
        tenantObj = appObj.objectStore.executeInsideTransaction(someFn)
        
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
      def dbfn(storeConnection):
        a = GetTenant(tenantName, storeConnection, 'a','b','c')
        if a is None:
          raise NotFound('Tenant Not Found')
        return a.getJSONRepresenation()
      return appObj.objectStore.executeInsideConnectionContext(dbfn)

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

        def someFn(connectionContext):
          return UpdateTenant(appObj, content['Name'], content['Description'], content['AllowUserCreation'],  content['AuthProviders'], content['ObjectVersion'], connectionContext)
        tenantObj = appObj.objectStore.executeInsideTransaction(someFn)
      
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
        def someFn(connectionContext):
          tenantObj = DeleteTenant(appObj, tenantName, objectVersion, connectionContext)
          return tenantObj.getJSONRepresenation()
        return appObj.objectStore.executeInsideTransaction(someFn)
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
      def dbfn(storeConnection):
        def defOutput(item):
          a = CreateUserObjFromUserDict(appObj, item[0],item[1],item[2],item[3], storeConnection).getJSONRepresenation()
          ##print("a:", a)
          return a

        try:
          outputFN = defOutput
          return GetPaginatedUserData(appObj, request, outputFN, storeConnection)
        except Exception as e:
          print(e)
          print(str(e.args))
          print(e.args)
          raise InternalServerError   
      return appObj.objectStore.executeInsideConnectionContext(dbfn)

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
      def dbfn(storeConnection):
        tenant = None
        if "mainTenant" in content:
          if content["mainTenant"] != "":
            tenant = content["mainTenant"]
            tenantObj = GetTenant(tenant, storeConnection, 'a','b','c')
            if tenantObj is None:
              raise BadRequest("Invalid tenant name")
        try:
          def someFn(connectionContext):
            CreateUser(appObj, userData, tenant, "adminapi/users/post", connectionContext)
            return GetUser(appObj, content["UserID"], connectionContext)
          userObj = storeConnection.executeInsideTransaction(someFn)
          
          
        except customExceptionClass as err:
          if (err.id=='TryingToCreateDuplicateUserException'):
            raise BadRequest(err.text)
          raise Exception('InternalServerError')
        except:
          raise InternalServerError
        
        return userObj.getJSONRepresenation(), 201
      return appObj.objectStore.executeInsideConnectionContext(dbfn)

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
      def dbfn(storeConnection):
        userObj = GetUser(appObj, userID, storeConnection)
        if userObj is None:
          raise NotFound('User Not Found')
        return userObj.getJSONRepresenation()
      return appObj.objectStore.executeInsideConnectionContext(dbfn)

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
        def someFn(connectionContext):
          return UpdateUser(
            appObj, 
            content['UserID'], 
            content['TenantRoles'], 
            content['known_as'],  
            content['other_data'], 
            content['ObjectVersion'],
            connectionContext
          )
        userObj = appObj.objectStore.executeInsideTransaction(someFn)

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
        def someFn(connectionContext):
          return DeleteUser(appObj, userID, objectVersion, connectionContext)
        userObj = appObj.objectStore.executeInsideTransaction(someFn)
        
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

      try:
        def someFn(connectionContext):
          def defOutput(item):
            return CreatePersonObjFromUserDict(appObj, item[0],item[1],item[2],item[3], connectionContext).getJSONRepresenation()
          return GetPaginatedPersonData(appObj, request, defOutput, connectionContext)
        return appObj.objectStore.executeInsideTransaction(someFn)
        
        
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
        def someFn(connectionContext):
          personDict = CreatePerson(appObj, connectionContext, None, 'a','b','c')
          return GetPerson(appObj, personDict["guid"], connectionContext)
        personObj = appObj.objectStore.executeInsideTransaction(someFn)
        
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
      def dbfn(storeConnection):
        a = GetPerson(appObj, personGUID, storeConnection)
        if a is None:
          raise NotFound('Person Not Found')
        return a.getJSONRepresenation()
      return appObj.objectStore.executeInsideConnectionContext(dbfn)

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
        def someFn(connectionContext):
          return UpdatePerson(appObj, content['guid'], content['ObjectVersion'], connectionContext)
        personObj = appObj.objectStore.executeInsideTransaction(someFn)
        
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
        def someFn(connectionContext):
          return DeletePerson(appObj, personGUID, objectVersion, connectionContext, 'a','b','c')
        personObj = appObj.objectStore.executeInsideTransaction(someFn)
        
        
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
      def dbfn(storeConnection):
        personObj = GetPerson(appObj, content["personGUID"], storeConnection)
        if personObj is None:
          raise NotFound('Person Not Found')
        userObj = GetUser(appObj, userID, storeConnection)
        if userObj is None:
          raise NotFound('User Not Found')
        try:
          def someFn(connectionContext):
            return associateUserWithPerson(appObj, content["UserID"], content["personGUID"], connectionContext)
          storeConnection.executeInsideTransaction(someFn)
          
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
      return appObj.objectStore.executeInsideConnectionContext(dbfn)

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
        def someFn(connectionContext):
          RemoveUserAssociation(appObj, userID, personGUID, None, connectionContext) #Not deleting person if this is last user
          return {
            "UserID": userID,
            "personGUID": personGUID
          }
        return appObj.objectStore.executeInsideTransaction(someFn)
        
        
      except customExceptionClass as err:
        if (err.id=='personDosentExistException'):
          raise BadRequest(err.text)
        if (err.id=='userDosentExistException'):
          raise BadRequest(err.text)
        raise Exception('InternalServerError')
      except:
        raise InternalServerError
     
  @nsAdmin.route('/<string:tenant>/auths')
  class authsInfo(Resource):
    
    @nsAdmin.doc('post Auth')
    @nsAdmin.expect(getCreateAuthModel(appObj), validate=True)
    @appObj.flastRestPlusAPIObject.response(400, 'Validation error')
    @appObj.flastRestPlusAPIObject.response(201, 'Created')
    @appObj.flastRestPlusAPIObject.marshal_with(getAuthModel(appObj), code=200, description='Auth created', skip_none=True)
    @nsAdmin.response(403, 'Forbidden - User dosen\'t have required role')
    def post(self, tenant):
      '''Create Auth'''
      verifySecurityOfAdminAPICall(appObj, request, tenant)
      content = request.get_json()
      requiredInPayload(content, ["personGUID", "authProviderGUID", "credentialJSON", "tenantName"])
      try:

        def someFn(connectionContext):
          authData = AddAuthForUser(appObj, content["tenantName"], content["authProviderGUID"], content["personGUID"], content["credentialJSON"], connectionContext)
          resp = {
            "personGUID": authData["personGUID"],
            "tenantName": content["tenantName"],
            "authProviderGUID": authData["AuthProviderGUID"],
            "AuthUserKey": authData["AuthUserKey"]
          }
          return resp, 201
        return appObj.objectStore.executeInsideTransaction(someFn)
        
      except customExceptionClass as err:
        if (err.id=='tenantDosentExistException'):
          raise BadRequest(err.text)
        if (err.id=='personDosentExistException'):
          raise BadRequest(err.text)
        if (err.id=='authProviderNotFoundException'):
          raise BadRequest(err.text)
        if (err.id=='InvalidAuthConfigException'):
          raise BadRequest(err.text)
        if (err.id=='tryingToCreateDuplicateAuthException'):
          raise BadRequest(err.text)
        raise Exception('InternalServerError')
      except:
        raise InternalServerError
     
  @nsAdmin.route('/<string:tenant>/auths/<string:authUserKeyEncoded>')
  class authInfo(Resource):
    @nsAdmin.doc('delete auth')
    @nsAdmin.response(200, 'auth Deleted')
    @nsAdmin.response(400, 'Error')
    @nsAdmin.response(403, 'Forbidden - User dosen\'t have required role')
    @nsAdmin.response(409, 'Conflict')
    @appObj.flastRestPlusAPIObject.marshal_with(getAuthModel(appObj), code=200, description='auth Deleted')
    def delete(self, tenant, authUserKeyEncoded):
      '''Delete auth'''
      decodedTokenObj = verifySecurityOfAdminAPICall(appObj, request, tenant)
      #No Object version needed for auths
      authUserKey = base64.b64decode(authUserKeyEncoded).decode('utf-8')
      def dbfn(storeConnection): 
        authData, objVer, creationDateTime, lastUpdateDateTime = getAuthRecord(appObj, authUserKey, storeConnection)
        if authData is None:
          raise BadRequest('Bad auth')
        try:
          
          def someFn(connectionContext):
            deleteAuthAndUnassiciateFromPerson(appObj, authData["personGUID"], authUserKey, connectionContext)
            resp = {
              "personGUID": authData["personGUID"],
              "tenantName": authData["tenantName"],
              "authProviderGUID": authData["AuthProviderGUID"],
              "AuthUserKey": authData["AuthUserKey"]
            }
            return resp, 200
          return storeConnection.executeInsideTransaction(someFn)
          
        except customExceptionClass as err:
          if (err.id=='personDosentExistException'):
            raise BadRequest(err.text)
          if (err.id=='userDosentExistException'):
            raise BadRequest(err.text)
          raise Exception('InternalServerError')
        except:
          raise InternalServerError    
      return appObj.objectStore.executeInsideConnectionContext(dbfn)