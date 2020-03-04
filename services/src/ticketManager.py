# Provides ticket manager class to manage tickets
import repositoryTicketType
import object_store_abstraction
import tenants
from werkzeug.exceptions import BadRequest


class ticketManagerClass():
  repositoryTicketType = None

  def __init__(self):
    self.repositoryTicketType = repositoryTicketType.TicketTypeRepositoryClass()

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