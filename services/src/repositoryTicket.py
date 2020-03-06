from object_store_abstraction import RepositoryBaseClass, RepositoryValidationException
from repositoryTicketObj import factoryFn as ticketObjFactoryFn
import constants

class TicketRepositoryClass(RepositoryBaseClass):
  objName = "Ticket"

  def __init__(self):
    RepositoryBaseClass.__init__(self, "tickets", ticketObjFactoryFn)


  def issueTicket(self, ForeignKey, typeGUID, expiry, storeConnection):
    ticketDict = {
      #"id": don't have to put it in as it is added by the base class
      "typeGUID": typeGUID,
      "expiry": expiry.isoformat(),
      "foreignKey": ForeignKey,
      "usedDate": None,
      "useWithUserID": None,
      "reissueRequestedDate": None,
      "reissuedTicketID": None,
      "disabled": False
    }
    (objID, objectVersion) = self.upsert(ticketDict, None, storeConnection=storeConnection)
    return (objID, objectVersion)