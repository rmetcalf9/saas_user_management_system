import apiSharedModels
from flask import request
from flask_restplus import Resource, marshal
import constants
from werkzeug.exceptions import InternalServerError, BadRequest, NotFound
import object_store_abstraction
from baseapp_for_restapi_backend_with_swagger import getPaginatedParamValues

def requiredInPayload(content, fieldList):
  for a in fieldList:
    if a not in content:
      raise BadRequest(a + ' not in payload')

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
      '''Get list of ticket types'''
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
      content_raw = request.get_json()
      content = marshal(content_raw, apiSharedModels.getCreateTicketTypeModel(appObj))


      #requiredInPayload(content, ['Name','Description','AllowUserCreation'])
      try:
        if object_store_abstraction.RepositoryObjBaseClass.getMetadataElementKey() in content_raw:
          raise object_store_abstraction.RepositoryValidationException(object_store_abstraction.RepositoryObjBaseClass.getMetadataElementKey() + " key should not be present when creating")
        if "id" in content_raw:
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

    @nsAdmin.doc('update Ticket Type')
    @nsAdmin.expect(apiSharedModels.getTicketTypeModel(appObj), validate=True)
    @appObj.flastRestPlusAPIObject.response(400, 'Validation error')
    @appObj.flastRestPlusAPIObject.marshal_with(apiSharedModels.getTicketTypeModel(appObj), code=202, description='Ticket Type updated', skip_none=True)
    @nsAdmin.response(403, 'Forbidden - User does not have required role')
    def post(self, tenant, tenantName, tickettypeID):
      ''' Update Ticket Type  '''
      APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)
      content_raw = request.get_json()
      content = marshal(content_raw, apiSharedModels.getTicketTypeModel(appObj))

      def dbfn(storeConnection):
        return appObj.TicketManager.updateTicketType(
          tenantName=tenantName,
          tickettypeID=tickettypeID,
          ticketTypeDict=content,
          storeConnection=storeConnection,
          appObj=appObj
        ).getDict(), 202
      try:
        return appObj.objectStore.executeInsideTransaction(dbfn)
      except object_store_abstraction.RepositoryValidationException as e:
        raise BadRequest(str(e))
      except object_store_abstraction.WrongObjectVersionExceptionClass as err:
        raise Conflict(err)

    @nsAdmin.doc('Delete TicketType')
    @appObj.flastRestPlusAPIObject.response(400, 'Validation error')
    @appObj.flastRestPlusAPIObject.marshal_with(apiSharedModels.responseModel(appObj), code=202, description='Ticket Type deleted', skip_none=True)
    @nsAdmin.response(403, 'Forbidden - User does not have required role')
    def delete(self, tenant, tenantName, tickettypeID):
      ''' Delete Ticket Type  '''
      APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)
      if "objectversion" not in request.args:
        raise BadRequest("Must supply object version to delete")
      if request.args["objectversion"] == None:
        raise BadRequest("Must supply object version to delete - can not be blank")
      objVer = None
      #if request.args["objectversion"] != 'LOOKUP': May need to add ability to lookup
      objVer = request.args["objectversion"]

      def dbfn(storeConnection):
        return appObj.TicketManager.deleteTicketType(tenantName=tenantName, tickettypeID=tickettypeID, ObjectVersionNumber=objVer, storeConnection=storeConnection)
      try:
        return appObj.objectStore.executeInsideTransaction(dbfn)
      except object_store_abstraction.RepositoryValidationException as err:
        return {"response": "ERROR", "message": str(err)}, 400
      except object_store_abstraction.WrongObjectVersionExceptionClass as err:
        return { "response": "ERROR", "message": str(err) }, 409 #not using standard exception as it gives html response
        #raise Conflict(err)

  @nsAdmin.route('/<string:tenant>/tenants/<string:tenantName>/tickettypes/<string:tickettypeID>/createbatch')
  class tickettypeCreateBatch(Resource):
    '''Ticket Type Process - Create Batch'''

    @nsAdmin.doc('run Ticket Type create Batch process')
    @nsAdmin.expect(apiSharedModels.getTicketTypeCreateBatchProcessModel(appObj), validate=True)
    @appObj.flastRestPlusAPIObject.response(400, 'Validation error')
    @appObj.flastRestPlusAPIObject.response(200, 'Completed')
    @appObj.flastRestPlusAPIObject.marshal_with(apiSharedModels.getTicketTypeCreateBatchProcessResponseModel(appObj), code=200, description='Ticket Type process complete', skip_none=True)
    @nsAdmin.response(403, 'Forbidden - User dosen\'t have required role')
    def post(self, tenant, tenantName, tickettypeID):
      '''Create Ticket Batch Process'''
      APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)
      content_raw = request.get_json()
      content = marshal(content_raw, apiSharedModels.getTicketTypeCreateBatchProcessModel(appObj))

      requiredInPayload(content, ['foreignKeyDupAction', 'foreignKeyList'])
      if not isinstance(content["foreignKeyList"], list):
        raise BadRequest('Bad foreignKeyList')
      if not isinstance(content["foreignKeyDupAction"], str):
        raise BadRequest('Bad foreignKeyDupAction')
      if "ReissueAll" not in content["foreignKeyDupAction"]:
        if "Skip" not in content["foreignKeyDupAction"]:
          raise BadRequest('Unknown foreignKeyDupAction')
      try:
        def someFn(storeConnection):
          (responseDict, responseStatus) = appObj.TicketManager.createBatchProcess(
            tenantName=tenantName,
            tickettypeID=tickettypeID,
            foreignKeyDupAction=content["foreignKeyDupAction"],
            foreignKeyList=content["foreignKeyList"],
            storeConnection=storeConnection,
            appObj=appObj
          )
          return responseDict, responseStatus
        return appObj.objectStore.executeInsideTransaction(someFn)

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

  @nsAdmin.route('/<string:tenant>/tenants/<string:tenantName>/tickettypes/<string:tickettypeID>/tickets')
  class tickettypeticketsInfo(Resource):
    '''Tickets'''

    @nsAdmin.doc('get Tickets')
    @nsAdmin.marshal_with(appObj.getResultModel(apiSharedModels.getTicketWithCaculatedFieldsModel(appObj)))
    @nsAdmin.response(200, 'Success', model=appObj.getResultModel(apiSharedModels.getTicketWithCaculatedFieldsModel(appObj)))
    @nsAdmin.response(401, 'Unauthorized')
    @nsAdmin.response(403, 'Forbidden - User dosen\'t have required role')
    @appObj.addStandardSortParams(nsAdmin)
    def get(self, tenant, tenantName, tickettypeID):
      '''Get list of tickets'''
      APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)
      paginatedParamValues = object_store_abstraction.sanatizePaginatedParamValues(getPaginatedParamValues(request))
      try:
        def outputFunction(itemObj):
          return itemObj.getDictWithCaculatedFields()
        def dbfn(storeConnection):
          return appObj.TicketManager.getTicketPaginatedResults(
            tenantName=tenantName,
            tickettypeID=tickettypeID,
            paginatedParamValues=paginatedParamValues,
            outputFN=outputFunction,
            storeConnection=storeConnection
          )
        return appObj.objectStore.executeInsideConnectionContext(dbfn)
      except:
        raise InternalServerError

  @nsAdmin.route('/<string:tenant>/tenants/<string:tenantName>/tickettypes/<string:tickettypeID>/tickets/disablebatch')
  class tickettypeticketsDisableProcess(Resource):
    '''Disable Ticket'''

    @nsAdmin.doc('disable batch of tickets')
    @nsAdmin.expect(apiSharedModels.getTicketDisableBatchProcessModel(appObj), validate=True)
    @appObj.flastRestPlusAPIObject.response(400, 'Validation error')
    @appObj.flastRestPlusAPIObject.response(200, 'Completed')
    @appObj.flastRestPlusAPIObject.marshal_with(apiSharedModels.getTicketDisableBatchProcessResponseModel(appObj), code=200, description='Ticket disable process complete', skip_none=True)
    @nsAdmin.response(403, 'Forbidden - User dosen\'t have required role')
    def post(self, tenant, tenantName, tickettypeID):
      '''Disable Ticket'''
      APIAdminCommon.verifySecurityOfAdminAPICall(appObj, request, tenant)
      content_raw = request.get_json()
      content = marshal(content_raw, apiSharedModels.getTicketDisableBatchProcessModel(appObj))

      requiredInPayload(content, ['tickets'])
      def dbfn(storeConnection):
        return appObj.TicketManager.disableTicketBatch(
          tenantName=tenantName,
          tickettypeID=tickettypeID,
          ticketsToDisable=content,
          storeConnection=storeConnection
        )
        #return ticketTypeObj.getDict(), 200
      return appObj.objectStore.executeInsideTransaction(dbfn)

