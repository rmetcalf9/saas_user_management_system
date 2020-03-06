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
      "fklu": {}
    }

  def getTicketIDFromForeignKey(self, foreignKey):
    if foreignKey not in self.getDict()["fklu"]:
      return None
    return self.obj["fklu"][foreignKey]

  def registerTicketIssuance(self, ForeignKey, ticketGUID):
    self.obj["fklu"][ForeignKey] = ticketGUID

  def registerTicketReIssuance(self, ForeignKey, ticketGUID):
    self.obj["fklu"][ForeignKey] = ticketGUID

