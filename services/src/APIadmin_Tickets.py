import apiSharedModels
from flask import request
from flask_restplus import Resource
import constants
from werkzeug.exceptions import InternalServerError, BadRequest, NotFound
import object_store_abstraction
from baseapp_for_restapi_backend_with_swagger import getPaginatedParamValues

def registerAPI(appObj, APIAdminCommon, nsAdmin):
  @nsAdmin.route('/<string:tenant>/tenants/<string:tenantName>/tickettypes')
  class tickettypesInfo(Resource):
    '''Ticket Types'''

    @nsAdmin.doc('get Ticket Types')
    @nsAdmin.marshal_with(appObj.getResultModel(apiSharedModels.getTicketTypeModel(appObj)))
    @nsAdmin.response(200, 'Success', model=appObj.getResultModel(apiSharedModels.getTicketTypeModel(appObj)))
    @nsAdmin.response(401, 'Unauthorized')
    @nsAdmin.response(403, 'Forbidden - User dosen\'t have required role')
    @appObj.addStandardSortParams(nsAdmin)
    def get(self, tenant, tenantName):
      '''Get list of tenants'''
      APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)
      paginatedParamValues = object_store_abstraction.sanatizePaginatedParamValues(getPaginatedParamValues(request))
      try:
        def outputFunction(itemObj):
          return itemObj.getDict()
        def dbfn(storeConnection):
          return appObj.TicketManager.getTicketTypePaginatedResults(
            tenantName=tenantName,
            paginatedParamValues=paginatedParamValues,
            outputFN=outputFunction,
            storeConnection=storeConnection
          )
        return appObj.objectStore.executeInsideConnectionContext(dbfn)
      except:
        raise InternalServerError

    @nsAdmin.doc('post Ticket Type')
    @nsAdmin.expect(apiSharedModels.getCreateTicketTypeModel(appObj), validate=True)
    @appObj.flastRestPlusAPIObject.response(400, 'Validation error')
    @appObj.flastRestPlusAPIObject.response(201, 'Created')
    @appObj.flastRestPlusAPIObject.marshal_with(apiSharedModels.getTicketTypeModel(appObj), code=200, description='Ticket Type created', skip_none=True)
    @nsAdmin.response(403, 'Forbidden - User dosen\'t have required role')
    def post(self, tenant, tenantName):
      '''Create Ticket Type'''
      APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)
      content = request.get_json()
      #requiredInPayload(content, ['Name','Description','AllowUserCreation'])
      try:
        if object_store_abstraction.RepositoryObjBaseClass.getMetadataElementKey() in content:
          raise object_store_abstraction.RepositoryValidationException(object_store_abstraction.RepositoryObjBaseClass.getMetadataElementKey() + " key should not be present when creating")
        if "id" in content:
          raise object_store_abstraction.RepositoryValidationException("id key should not be present when creating")
        def someFn(storeConnection):
          return appObj.TicketManager.upsertTicketType(
            tenantName=tenantName,
            ticketTypeDict=content,
            objectVersion=None,
            storeConnection=storeConnection,
            appObj=appObj)
        ticketTypeObj = appObj.objectStore.executeInsideTransaction(someFn)

      except constants.customExceptionClass as err:
        #if (err.id=='tenantAlreadtExistsException'):
        #  raise BadRequest(err.text)
        raise Exception('InternalServerError')
      except object_store_abstraction.RepositoryValidationException as e:
        raise BadRequest(str(e))
      except BadRequest as e:
        raise e
      except:
        raise InternalServerError

      return ticketTypeObj.getDict(), 201

  @nsAdmin.route('/<string:tenant>/tenants/<string:tenantName>/tickettypes/<string:tickettypeID>')
  class tickettypeInfo(Resource):
    '''Ticket Type'''

    @nsAdmin.doc('get Ticket Type')
    @nsAdmin.marshal_with(apiSharedModels.getTicketTypeModel(appObj))
    @nsAdmin.response(200, 'Success', model=apiSharedModels.getTicketTypeModel(appObj))
    @nsAdmin.response(401, 'Unauthorized')
    @nsAdmin.response(403, 'Forbidden - User does not have required role')
    @nsAdmin.response(404, 'TicketType Not Found')
    def get(self, tenant, tenantName, tickettypeID):
      '''Get Ticket Type'''
      APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)
      def dbfn(storeConnection):
        ticketTypeObj = appObj.TicketManager.getTicketType(tenantName=tenantName, tickettypeID=tickettypeID, storeConnection=storeConnection)
        if ticketTypeObj is None:
          return NotFound, 404
        return ticketTypeObj.getDict(), 200
      return appObj.objectStore.executeInsideTransaction(dbfn)

