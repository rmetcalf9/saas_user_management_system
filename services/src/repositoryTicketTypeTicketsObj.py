from object_store_abstraction import RepositoryObjBaseClass
import uuid

def factoryFn(obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj, storeConnection):
  return TicketTypeTicketsObjClass(obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj=repositoryObj, storeConnection=storeConnection)

class TicketTypeTicketsObjClass(RepositoryObjBaseClass):
  def __init__(self, obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj, storeConnection):
    RepositoryObjBaseClass.__init__(self, obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj)

  @classmethod
  def getNewTicketDict(cls, ticketTypeID):
    return {
      "id": ticketTypeID,
      "fklu": {}, #foreign key lookup
      "at": [] #All ticket guids for this ticketype
    }

  def getTicketIDFromForeignKey(self, foreignKey):
    if foreignKey not in self.getDict()["fklu"]:
      return None
    return self.obj["fklu"][foreignKey]

  def registerTicketIssuance(self, ForeignKey, ticketGUID):
    self.obj["fklu"][ForeignKey] = ticketGUID
    self.obj["at"].append(ticketGUID)

  def registerTicketReIssuance(self, ForeignKey, newTicketGUID):
    self.obj["fklu"][ForeignKey] = newTicketGUID
    self.obj["at"].append(newTicketGUID)

  def getAllTicketGUIDSForThisType(self):
    return self.obj["at"]