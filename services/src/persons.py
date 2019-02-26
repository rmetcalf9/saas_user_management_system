#Code for representing a person
# A person can have one or many Auths
# A person has access to many identities
import uuid
from personObj import personClass
from constants import customExceptionClass
from objectStores_base import WrongObjectVersionExceptionClass

personDosentExistException = customExceptionClass('Person not found', 'personDosentExistException')

# One Person can have many Auths
#Use store object Persons to store individual person information
# The Auth has a personID stored in it
# use store object AuthsForEachPerson to store list of auths for each person

def CreatePerson(appObj):
  guid = str(uuid.uuid4())
  personDict = {
    'guid': guid
  }
  appObj.objectStore.saveJSONObject(appObj, "Persons", guid, personDict)
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

def GetPerson(appObj, personGUID):
  personDICT, objVer, creationDateTime, lastUpdateDateTime = appObj.objectStore.getObjectJSON(appObj,"Persons", personGUID)
  if personDICT is None:
    return None
  personObj = personClass(personDICT, objVer, creationDateTime, lastUpdateDateTime)
  return personObj

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
  #may not have object version check (cascades don't)
  #not cascading delete down to users
  personObj = GetPerson(appObj, personGUID)
  if personObj is None:
    raise personDosentExistException

  appObj.objectStore.removeJSONObject(appObj, "Persons", personGUID, objectVersion)
  
  authsForThisGUID, objVer, creationDateTime, lastUpdateDateTime = appObj.objectStore.getObjectJSON(appObj,"AuthsForEachPerson", personGUID)

  appObj.objectStore.removeJSONObject(appObj, "AuthsForEachPerson", personGUID, ignoreMissingObject=True)
  
  if authsForThisGUID is not None:
    for authKey in authsForThisGUID:
      return appObj.objectStore.removeJSONObject(appObj, "userAuths", authKey)
  return personObj
  
def GetPaginatedPersonData(appObj, request, outputFN, filterFN):
  return appObj.objectStore.getPaginatedResult(appObj, "Persons",  appObj.getPaginatedParamValues(request), request, outputFN, filterFN)

