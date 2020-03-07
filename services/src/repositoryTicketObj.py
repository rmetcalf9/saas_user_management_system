from object_store_abstraction import RepositoryObjBaseClass
from dateutil.parser import parse

def factoryFn(obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj, storeConnection):
  return TicketObjClass(obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj=repositoryObj, storeConnection=storeConnection)

class TicketObjClass(RepositoryObjBaseClass):
  def __init__(self, obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj, storeConnection):
    RepositoryObjBaseClass.__init__(self, obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj)

  def containsQueryString(self, upperCaseQueryString):
    if self.obj["foreignKey"].upper().find(upperCaseQueryString) != -1:
      return True
    if self.getUsableState() == upperCaseQueryString:
      return True
    return False

  def getUsableState(self):
    ##DISABLED, REISSUED, ALREADYUSED, EXPIRED or USABLEIFTICKETTYPEISENABLED
    # USABLEIFTICKETTYPEISENABLED reminds to do extra check when using

    if self.getDict()["disabled"]:
      return "US_DISABLED"
    if self.getDict()["reissuedTicketID"] is not None:
      return "US_REISSUED"
    if self.getDict()["useWithUserID"] is not None:
      return "US_ALREADYUSED"
    dt = parse(self.getDict()["expiry"])
    if self.repositoryObj.appObj.getCurDateTime() > dt:
      return "US_EXPIRED"

    return "US_USABLEIFTICKETTYPEISENABLED"

  def getDictWithCaculatedFields(self):
    resDict = self.getDict()
    resDict["usableState"] = self.getUsableState()
    return resDict

  def disable(self):
    # if it is already disabled then just ignore
    self.getDict()["disabled"] = True