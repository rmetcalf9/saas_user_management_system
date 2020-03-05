from object_store_abstraction import RepositoryObjBaseClass

def factoryFn(obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj, storeConnection):
  return TickertTypeObjClass(obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj=repositoryObj, storeConnection=storeConnection)

class TickertTypeObjClass(RepositoryObjBaseClass):
  def __init__(self, obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj, storeConnection):
    RepositoryObjBaseClass.__init__(self, obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj)

  def containsQueryString(self, upperCaseQueryString):
    # id: GUID for ticket Type
    # tenantName: tenant this ticket is valid for
    # ticketTypeName: for admin screens
    # description: for admin screens
    if self.obj["id"].upper().find(upperCaseQueryString) != -1:
      return True
    #Not filtering on tenant name as the query can only be for a single tenant so
    # it dosen't make sense
    #if self.obj["tenantName"].upper().find(upperCaseQueryString) != -1:
    #  return True
    if self.obj["ticketTypeName"].upper().find(upperCaseQueryString) != -1:
      return True
    if self.obj["description"].upper().find(upperCaseQueryString) != -1:
      return True
    return False
