from object_store_abstraction import RepositoryObjBaseClass

def factoryFn(obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj, storeConnection):
  return TicketObjClass(obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj=repositoryObj, storeConnection=storeConnection)

class TicketObjClass(RepositoryObjBaseClass):
  def __init__(self, obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj, storeConnection):
    RepositoryObjBaseClass.__init__(self, obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj)

  def containsQueryString(self, upperCaseQueryString):
    if self.obj["foreignKey"].upper().find(upperCaseQueryString) != -1:
      return True
    return False