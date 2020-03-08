# Provides ticket manager class to manage tickets
import repositoryTicket
import repositoryTicketTypeTickets
import repositoryTicketTypeTicketsObj
import repositoryTicketType
import object_store_abstraction
import tenants
from werkzeug.exceptions import BadRequest, NotFound
import datetime
import pytz

class ticketManagerClass():
  repositoryTicketType = None
  repositoryTicket = None
  repositoryTicketTypeTickets = None

  def __init__(self, appObj):
    self.repositoryTicketType = repositoryTicketType.TicketTypeRepositoryClass()
    self.repositoryTicket = repositoryTicket.TicketRepositoryClass(appObj)
    self.repositoryTicketTypeTickets = repositoryTicketTypeTickets.TicketTypeTicketsRepositoryClass()

  def updateTicketType(self, tenantName, tickettypeID, ticketTypeDict, storeConnection, appObj):
    if ticketTypeDict["id"] != tickettypeID:
      raise BadRequest("URL and data ID mismatch")
    object_store_abstraction.RepositoryBaseClass.RequireStringElement(ticketTypeDict, object_store_abstraction.RepositoryObjBaseClass.getMetadataElementKey(), "TicketType")
    curObj = self.getTicketType(tenantName, tickettypeID, storeConnection=storeConnection)
    if curObj is None:
      raise NotFound("Ticket Type not found")

    return self.upsertTicketType(tenantName, ticketTypeDict, ticketTypeDict[object_store_abstraction.RepositoryObjBaseClass.getMetadataElementKey()]["objectVersion"], storeConnection, appObj)

  def upsertTicketType(self, tenantName, ticketTypeDict, objectVersion, storeConnection, appObj):
    object_store_abstraction.RepositoryBaseClass.RequireStringElement(ticketTypeDict, "tenantName", "TicketType")
    if tenantName != ticketTypeDict["tenantName"]:
      raise BadRequest("Tenant URL and Data mismatch")
    tenantObj = tenants.GetTenant(ticketTypeDict["tenantName"], storeConnection, appObj=appObj)
    if tenantObj is None:
      raise tenants.tenantDosentExistException
    objID, objectVersion = self.repositoryTicketType.upsert(ticketTypeDict, objectVersion, storeConnection)
    return self.repositoryTicketType.get(id=objID, storeConnection=storeConnection)

  def getTicketType(self, tenantName, tickettypeID, storeConnection):
    retObj = self.repositoryTicketType.get(id=tickettypeID, storeConnection=storeConnection)
    if retObj is None:
      return None
    if retObj.obj["tenantName"] != tenantName:
      return None
    return retObj

  def getTicketTypePaginatedResults(self, tenantName, paginatedParamValues, outputFN, storeConnection):
    def filterFn(obj, whereClauseText):
      if obj.obj["tenantName"] != tenantName:
        return False
      if whereClauseText is None:
        return True
      if whereClauseText == "":
        return True
      # I want to combine clauses using AND
      for curWhereClause in whereClauseText.split(" "):
        if not obj.containsQueryString(upperCaseQueryString=curWhereClause.upper()):
          return False
      return True
    return self.repositoryTicketType.getPaginatedResult(paginatedParamValues, outputFN, storeConnection, filterFn)

  def getTicketPaginatedResults(self, tenantName, tickettypeID, paginatedParamValues, outputFN, storeConnection):
    ticketObj = self.getTicketType(tenantName, tickettypeID=tickettypeID, storeConnection=storeConnection)
    if ticketObj is None:
      return {"response": "ERROR", "message": "Ticket type not found in this tenant"}, 404

    def filterFn(obj, whereClauseText):
      if obj.getDict()["typeGUID"] != ticketObj.getDict()["id"]:
        return False
      if whereClauseText is None:
        return True
      if whereClauseText == "":
        return True
      for curWhereClause in whereClauseText.split(" "):
        if obj.containsQueryString(upperCaseQueryString=curWhereClause.upper()):
          return True
      return False
    return self.repositoryTicket.getPaginatedResult(paginatedParamValues, outputFN, storeConnection, filterFn)

  def deleteTicketType(self, tenantName, tickettypeID, ObjectVersionNumber, storeConnection):
    ticketTypeObj = self.getTicketType(tenantName, tickettypeID=tickettypeID, storeConnection=storeConnection)
    if ticketTypeObj is None:
      return {"response": "ERROR", "message": "Ticket type not found in this tenant"}, 404
    #Early Object version check to stop any actions being taken if object version is wrong
    if str(ObjectVersionNumber) != str(ticketTypeObj.getDict()[object_store_abstraction.RepositoryObjBaseClass.getMetadataElementKey()]["objectVersion"]):
      raise object_store_abstraction.WrongObjectVersionException

    ticketTypeTicketsObj = self.repositoryTicketTypeTickets.get(id=tickettypeID, storeConnection=storeConnection)
    print("*************** ticketTypeTicketsObj", ticketTypeTicketsObj, tickettypeID)
    if ticketTypeTicketsObj is not None:
      #There were tickets for this ticket type

      for ticketGUID in ticketTypeTicketsObj.getAllTicketGUIDSForThisType():
        self.repositoryTicket.remove(id=ticketGUID, storeConnection=storeConnection, objectVersion=None)
      self.repositoryTicketTypeTickets.remove(id=tickettypeID, storeConnection=storeConnection, objectVersion=ticketTypeTicketsObj.getDict()[object_store_abstraction.RepositoryObjBaseClass.getMetadataElementKey()]["objectVersion"])


    self.repositoryTicketType.remove(id=tickettypeID, storeConnection=storeConnection, objectVersion=ObjectVersionNumber)
    return {"response": "OK"}, 202

  def createBatchProcess(self, tenantName, tickettypeID, foreignKeyDupAction, foreignKeyList, storeConnection, appObj):
    #print("createBatchProcess", foreignKeyList)
    ticketTypeObj = self.getTicketType(tenantName, tickettypeID=tickettypeID, storeConnection=storeConnection)
    if ticketTypeObj is None:
      return {"response": "ERROR", "message": "Ticket Type not found in this tenant"}, 404
    issued = 0
    reissued = 0
    skipped = 0
    results = []

    ticketTypeTicketsObj = self.repositoryTicketTypeTickets.get(id=tickettypeID, storeConnection=storeConnection)
    if ticketTypeTicketsObj is None:
      ticketTypeTicketsObj = repositoryTicketTypeTicketsObj.factoryFn(
        obj=repositoryTicketTypeTicketsObj.TicketTypeTicketsObjClass.getNewTicketDict(ticketTypeID=tickettypeID),
        objVersion=None,
        creationDateTime=appObj.getCurDateTime(),
        lastUpdateDateTime=appObj.getCurDateTime(),
        objKey=tickettypeID,
        repositoryObj=self.repositoryTicketTypeTickets,
        storeConnection=storeConnection
      )
    for curForeignKey in foreignKeyList:
      existingTicketID = ticketTypeTicketsObj.getTicketIDFromForeignKey(foreignKey=curForeignKey)
      if existingTicketID is None:
        (ticketGUID, _) = self.repositoryTicket.issueTicket(
          ForeignKey=curForeignKey,
          typeGUID=tickettypeID,
          expiry=appObj.getCurDateTime() + datetime.timedelta(hours=int(ticketTypeObj.getDict()["issueDuration"])),
          storeConnection=storeConnection
        )
        ticketTypeTicketsObj.registerTicketIssuance(ForeignKey=curForeignKey, ticketGUID=ticketGUID)
        results.append({ "foreignKey": curForeignKey, "ticketGUID": ticketGUID })
        issued += 1
      else:
        # Foreign key is in use for this ticket type
        if foreignKeyDupAction == "Skip":
          skipped += 1
        else:
          #In reissue mode, need to reissue the ticket
          (ticketGUID, _) = self.repositoryTicket.reissueTicket(
            ForeignKey=curForeignKey,
            existingTicketGUID=existingTicketID,
            typeGUID=tickettypeID,
            newexpiry=appObj.getCurDateTime() + datetime.timedelta(hours=int(ticketTypeObj.getDict()["issueDuration"])),
            storeConnection=storeConnection
          )
          ticketTypeTicketsObj.registerTicketReIssuance(ForeignKey=curForeignKey, newTicketGUID=ticketGUID)
          results.append({"foreignKey": curForeignKey, "ticketGUID": ticketGUID})
          reissued += 1

    objID, objectVersion = ticketTypeTicketsObj.save(storeConnection=storeConnection)
    # print("Saved ticket Type Ticket", objID)
    return {
      "results": results,
      "stats": {
        "issued": issued,
        "reissued": reissued,
        "skipped": skipped
      }
    }, 200

  def _disableTicket(self, ticketTypeObj, ticketObj, disableInputData, storeConnection):
    if ticketObj is None:
      return {"ticketGUID": disableInputData["ticketGUID"], "response": "ERROR", "message": "Ticket not found"}
    if ticketObj.getDict()["typeGUID"] != ticketTypeObj.getDict()["id"]:
      return {"ticketGUID": disableInputData["ticketGUID"],"response": "ERROR", "message": "Ticket data mismatch"}
    try:
      ticketObj.disable()
      ticketObj.save(storeConnection=storeConnection)
    except Exception as e:
      return {"ticketGUID": disableInputData["ticketGUID"], "response": "ERROR", "message": "Exception - " + str(e)}

    return {"ticketGUID": disableInputData["ticketGUID"],"response": "OK", "message": "OK"}

  def disableTicketBatch(self,
    tenantName,
    tickettypeID,
    ticketsToDisable,
    storeConnection
  ):
    ticketTypeObj = self.getTicketType(tenantName, tickettypeID=tickettypeID, storeConnection=storeConnection)
    if ticketTypeObj is None:
      return {"response": "ERROR", "message": "Ticket type not found in this tenant", "results": []}, 404

    res = []
    for curTicket in ticketsToDisable["tickets"]:
      ticketObj = self.repositoryTicket.get(id=curTicket["ticketGUID"], storeConnection=storeConnection)
      res.append(self._disableTicket(ticketTypeObj=ticketTypeObj, ticketObj=ticketObj, disableInputData=curTicket, storeConnection=storeConnection))

    return { "response": "OK", "message": "OK", "results": res }, 200

