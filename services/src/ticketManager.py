# Provides ticket manager class to manage tickets
import repositoryTicketType

class ticketManagerClass():
  repositoryTicketType = None

  def __init__(self):
    self.repositoryTicketType = repositoryTicketType.TicketTypeRepositoryClass()

  def upsertTicketType(self, ticketTypeDict, objectVersion, storeConnection):
    return self.repositoryTicketType.upsert(ticketTypeDict, objectVersion, storeConnection)
