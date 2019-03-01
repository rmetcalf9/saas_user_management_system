#Code for representing a person
# A person can have one or many Auths
# A person has access to many identities
import uuid
from personObj import personClass
from constants import customExceptionClass
from objectStores_base import WrongObjectVersionExceptionClass
from userPersonCommon import RemoveUserAssociation, getListOfUserIDsForPersonNoTenantCheck, GetUser, personDosentExistException

# One Person can have many Auths
#Use store object Persons to store individual person information
# The Auth has a personID stored in it
# use store object AuthsForEachPerson to store list of auths for each person

#guidToUse only set in testing mode for the main defualt person
def CreatePerson(appObj, guidToUse = None):
  if guidToUse is None:
    guidToUse = str(uuid.uuid4())
  personDict = {
    'guid': guidToUse
  }
  appObj.objectStore.saveJSONObject(appObj, "Persons", guidToUse, personDict)
  return personDict

def associatePersonWithAuthCalledWhenAuthIsCreated(appObj, personGUID, AuthUserKey):
  def upd(idfea):
    if idfea is None:
      idfea = []
    if AuthUserKey in idfea:
      raise PersonAlreadyHasThisAuthException
    idfea.append(AuthUserKey)
    return idfea
  appObj.objectStore.updateJSONObject(appObj,"AuthsForEachPerson", personGUID, upd)

def CreatePersonObjFromUserDict(appObj, PersonDict, objVersion, creationDateTime, lastUpdateDateTime):
  AssociatedUserIDs = getListOfUserIDsForPersonNoTenantCheck(appObj, PersonDict['guid'])
  ##print("AAA:", AssociatedUserIDs, ":", personGUID)
  AssociatedUserObjs = []
  for uid in AssociatedUserIDs:
    AssociatedUserObjs.append(GetUser(appObj,uid))
  personObj = personClass(PersonDict, objVersion, creationDateTime, lastUpdateDateTime, AssociatedUserObjs)
  return personObj
  
def GetPerson(appObj, personGUID):
  personDICT, objVer, creationDateTime, lastUpdateDateTime = appObj.objectStore.getObjectJSON(appObj,"Persons", personGUID)
  if personDICT is None:
    return None
  return CreatePersonObjFromUserDict(appObj, personDICT, objVer, creationDateTime, lastUpdateDateTime)

def UpdatePerson(appObj, personGUID, objectVersion):
  #Can't currently update any person data but API added because we will in future
  personObj = GetPerson(appObj, personGUID)
  if personObj is None:
    raise personDosentExistException
  if str(personObj.getObjectVersion()) != str(objectVersion):
    raise WrongObjectVersionExceptionClass
    
  def updPerson(person):
    if person is None:
      raise personDosentExistException
    return person
  appObj.objectStore.updateJSONObject(appObj,"Persons", personGUID, updPerson, objectVersion)

  pObj = GetPerson(appObj, personGUID)
  return pObj

  
def DeletePerson(appObj, personGUID, objectVersion = None):
  userIDsThisPerson = getListOfUserIDsForPersonNoTenantCheck(appObj, personGUID)
  for userID in userIDsThisPerson:
    RemoveUserAssociation(appObj, userID, personGUID, None)
  
  #may not have object version check (cascades don't)
  #not cascading delete down to users
  personObj = GetPerson(appObj, personGUID)
  if personObj is None:
    raise personDosentExistException

  appObj.objectStore.removeJSONObject(appObj, "Persons", personGUID, objectVersion)
  
  authsForThisGUID, objVer, creationDateTime, lastUpdateDateTime = appObj.objectStore.getObjectJSON(appObj,"AuthsForEachPerson", personGUID)

  appObj.objectStore.removeJSONObject(appObj, "AuthsForEachPerson", personGUID, ignoreMissingObject=True)
  
  appObj.objectStore.removeJSONObject(appObj, "UsersForEachPerson", personGUID, None, ignoreMissingObject=True)

  
  if authsForThisGUID is not None:
    for authKey in authsForThisGUID:
      appObj.objectStore.removeJSONObject(appObj, "userAuths", authKey)
  return personObj
  
def GetPaginatedPersonData(appObj, request, outputFN):
  return appObj.objectStore.getPaginatedResult(appObj, "Persons",  appObj.getPaginatedParamValues(request), request, outputFN)

