from object_store_abstraction import RepositoryObjBaseClass
from dateutil.parser import parse

def factoryFn(obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj, storeConnection):
  return TicketObjClass(obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj=repositoryObj, storeConnection=storeConnection)

class TicketObjClass(RepositoryObjBaseClass):
  #Tickets are used either in the Register function or in the Login function
  # if a ticket is used for an auth like google then it will call the register function
  # before the login function gets to call it. This indicator prevents us trying to
  # use the ticket twice
  #  (It is different to set used)
  internalUseIndicator = None

  def __init__(self, obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj, storeConnection):
    RepositoryObjBaseClass.__init__(self, obj, objVersion, creationDateTime, lastUpdateDateTime, objKey, repositoryObj)
    self.internalUseIndicator = False

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

  def getUsable(self, ticketTypeObj):
    if not ticketTypeObj.isEnabled():
      return "INVALID"
    usState = self.getUsableState()
    if usState == "US_EXPIRED":
      return "EXPIRED"
    elif usState == "US_USABLEIFTICKETTYPEISENABLED":
      return "USABLE"
    return "INVALID"

  def setUsed(self, appObj, userID):
    self.internalUseIndicator = True #This is not stored in DB
    self.getDict()["useWithUserID"] = userID
    self.getDict()["usedDate"] = appObj.getCurDateTime().isoformat()
