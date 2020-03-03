from object_store_abstraction import RepositoryObjBaseClass

def factoryFn(obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj, storeConnection):
  return TickertTypeObjClass(obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj=repositoryObj, storeConnection=storeConnection)

class TickertTypeObjClass(RepositoryObjBaseClass):
  def __init__(self, obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj, storeConnection):
    RepositoryObjBaseClass.__init__(self, obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj)

