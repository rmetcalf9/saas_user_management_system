from object_store_abstraction import RepositoryObjBaseClass

def factoryFn(obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj, storeConnection):
  return TicketTypeTicketsObjClass(obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj=repositoryObj, storeConnection=storeConnection)

class TicketTypeTicketsObjClass(RepositoryObjBaseClass):
  def __init__(self, obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj, storeConnection):
    RepositoryObjBaseClass.__init__(self, obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj)

  @classmethod
  def getNewTicketDict(cls):
    return {
      "fklu": {}
    }

  def getTicketIDFromForeignKey(self, foreignKey):
    if "foreignKey" not in self.obj["fklu"]:
      return None
    return self.obj["fklu"]["foreignKey"]

  def registerTicketIssuance(self, ForeignKey, ticketGUID):
    self.obj["fklu"]["foreignKey"] = ticketGUID

  #candidate for putting into baseclass library
  def save(self, storeConnection):
    objID, objectVersion = self.repositoryObj.upsert(
      self.getDict(),
      self.getDict()[RepositoryObjBaseClass.getMetadataElementKey()]["objectVersion"],
      storeConnection
    )
    return (objID, objectVersion)
