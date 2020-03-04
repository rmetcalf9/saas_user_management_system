# Provides ticket manager class to manage tickets
import repositoryTicketType
import object_store_abstraction
import tenants

class ticketManagerClass():
  repositoryTicketType = None

  def __init__(self):
    self.repositoryTicketType = repositoryTicketType.TicketTypeRepositoryClass()

  def upsertTicketType(self, ticketTypeDict, objectVersion, storeConnection, appObj):
    object_store_abstraction.RepositoryBaseClass.RequireStringElement(ticketTypeDict, "tenantName", "TicketType")

    tenantObj = tenants.GetTenant(ticketTypeDict["tenantName"], storeConnection, appObj=appObj)
    if tenantObj is None:
      raise tenants.tenantDosentExistException

    return self.repositoryTicketType.upsert(ticketTypeDict, objectVersion, storeConnection)
