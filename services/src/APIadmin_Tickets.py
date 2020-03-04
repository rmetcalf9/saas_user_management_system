import apiSharedModels
from flask import request
from flask_restplus import Resource
import constants
from werkzeug.exceptions import InternalServerError, BadRequest
import object_store_abstraction

def registerAPI(appObj, APIAdminCommon, nsAdmin):
  @nsAdmin.route('/<string:tenant>/tenants/<string:tenantName>/tickettypes')
  class tickettypesInfo(Resource):
  #
  #   '''Admin'''
  #   @nsAdmin.doc('admin')
  #   @nsAdmin.marshal_with(appObj.getResultModel(getTenantModel(appObj)))
  #   @nsAdmin.response(200, 'Success', model=appObj.getResultModel(getTenantModel(appObj)))
  #   @nsAdmin.response(401, 'Unauthorized')
  #   @nsAdmin.response(403, 'Forbidden - User dosen\'t have required role')
  #   @appObj.addStandardSortParams(nsAdmin)
  #   def get(self, tenant):
  #     '''Get list of tenants'''
  #     APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)
  #
  #     paginatedParamValues = getPaginatedParamValues(request)
  #
  #     def defOutput(item):
  #       return tenantClass(item[0],item[1], appObj).getJSONRepresenation()
  #
  #     try:
  #       def dbfn(storeConnection):
  #         outputFN = defOutput
  #         return storeConnection.getPaginatedResult("tenants", paginatedParamValues, outputFN)
  #       return appObj.objectStore.executeInsideConnectionContext(dbfn)
  #     except:
  #       raise InternalServerError

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
      except:
        raise InternalServerError

      return ticketTypeObj.getDict(), 201