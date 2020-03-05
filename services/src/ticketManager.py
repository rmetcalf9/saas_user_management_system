# Provides ticket manager class to manage tickets
import repositoryTicketType
import object_store_abstraction
import tenants
from werkzeug.exceptions import BadRequest, NotFound


class ticketManagerClass():
  repositoryTicketType = None

  def __init__(self):
    self.repositoryTicketType = repositoryTicketType.TicketTypeRepositoryClass()

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

  def deleteTicketType(self, tenantName, tickettypeID, ObjectVersionNumber, storeConnection):
    ticketObj = self.getTicketType(tenantName, tickettypeID=tickettypeID, storeConnection=storeConnection)
    if ticketObj is None:
      return {"response": "ERROR", "message": "Ticket not found in this tenant"}, 404
    self.repositoryTicketType.remove(id=tickettypeID, storeConnection=storeConnection, objectVersion=ObjectVersionNumber)
    return {"response": "OK"}, 202
