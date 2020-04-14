from object_store_abstraction import RepositoryObjBaseClass

def factoryFn(obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj, storeConnection):
  return APIKeyObjClass(obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj=repositoryObj, storeConnection=storeConnection)

class APIKeyObjClass(RepositoryObjBaseClass):
  def __init__(self, obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj, storeConnection):
    RepositoryObjBaseClass.__init__(self, obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj)



  def getCreateDict(self, APIKey):
    return {
      "apikey": APIKey,
      "apikeydata": self.getDict()
    }

  def getTenant(self):
    return self.getDict()["tenantName"]

  def userCanRead(self, tenantName, userID):
    if tenantName != self.getTenant():
      return False
    return userID == self.getDict()["createdByUserID"]

