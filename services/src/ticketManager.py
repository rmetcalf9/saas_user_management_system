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

  def __init__(self):
    self.repositoryTicketType = repositoryTicketType.TicketTypeRepositoryClass()
    self.repositoryTicket = repositoryTicket.TicketRepositoryClass()
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
      for curWhereClause in whereClauseText.split(" "):
        if obj.containsQueryString(upperCaseQueryString=curWhereClause.upper()):
          return True
      return False
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
      if obj.containsQueryString(upperCaseQueryString=curWhereClause.upper()):
        return True
      return False
    return self.repositoryTicket.getPaginatedResult(paginatedParamValues, outputFN, storeConnection, filterFn)

  def deleteTicketType(self, tenantName, tickettypeID, ObjectVersionNumber, storeConnection):
    ticketObj = self.getTicketType(tenantName, tickettypeID=tickettypeID, storeConnection=storeConnection)
    if ticketObj is None:
      return {"response": "ERROR", "message": "Ticket type not found in this tenant"}, 404
    self.repositoryTicketType.remove(id=tickettypeID, storeConnection=storeConnection, objectVersion=ObjectVersionNumber)
    return {"response": "OK"}, 202

  def createBatchProcess(self, tenantName, tickettypeID, foreignKeyDupAction, foreignKeyList, storeConnection, appObj):
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
        obj=repositoryTicketTypeTicketsObj.TicketTypeTicketsObjClass.getNewTicketDict(),
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
        results.append({ "foreignkey": curForeignKey, "ticketGUID": ticketGUID })
        issued += 1
      else:
        raise Exception("Not Implemented")

    objID, objectVersion = ticketTypeTicketsObj.save(storeConnection=storeConnection)

    return {
      "results": results,
      "stats": {
        "issued": issued,
        "reissued": reissued,
        "skipped": skipped
      }
    }, 200