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

  def reissueTicket(self, ForeignKey, existingTicketGUID, typeGUID, newexpiry, storeConnection):
    origTicketObj = self.get(existingTicketGUID, storeConnection)
    if origTicketObj is None:
      raise Exception("Failed to find ticket")

    newTicketDict = {
      #"id": don't have to put it in as it is added by the base class
      "typeGUID": typeGUID,
      "expiry": newexpiry.isoformat(),
      "foreignKey": ForeignKey,
      "usedDate": None,
      "useWithUserID": None,
      "reissueRequestedDate": None,
      "reissuedTicketID": None,
      "disabled": False
    }
    (newTicketGUID, objectVersion) = self.upsert(newTicketDict, None, storeConnection=storeConnection)

    origTicketObj.getDict()["reissuedTicketID"] = newTicketGUID
    origTicketObj.save(storeConnection=storeConnection)

    return (newTicketGUID, objectVersion)
