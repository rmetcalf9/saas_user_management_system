#Code for representing a person
# A person can have one or many Auths
# A person has access to many identities
import uuid
from personObj import personClass
from constants import customExceptionClass
from objectStores_base import WrongObjectVersionExceptionClass
from userPersonCommon import RemoveUserAssociation, getListOfUserIDsForPersonNoTenantCheck, GetUser, personDosentExistException
from authsCommon import getAuthRecord, DeleteAuthRecord

# One Person can have many Auths
#Use store object Persons to store individual person information
# The Auth has a personID stored in it
# use store object AuthsForEachPerson to store list of auths for each person

#guidToUse only set in testing mode for the main defualt person
def CreatePerson(appObj, storeConnection, guidToUse, a,b,c):
  if guidToUse is None:
    guidToUse = str(uuid.uuid4())
  personDict = {
    'guid': guidToUse
  }
  storeConnection.saveJSONObject("Persons", guidToUse, personDict)
  return personDict

def associatePersonWithAuthCalledWhenAuthIsCreated(appObj, personGUID, AuthUserKey, storeConnection):
  def upd(idfea, transactionContext):
    if idfea is None:
      idfea = []
    if AuthUserKey in idfea:
      raise PersonAlreadyHasThisAuthException
    idfea.append(AuthUserKey)
    return idfea
  storeConnection.updateJSONObject("AuthsForEachPerson", personGUID, upd)

def deleteAuthAndUnassiciateFromPerson(appObj, personGUID, AuthUserKey):
  def upd(idfea, transactionContext):
    if idfea is not None:
      if AuthUserKey in idfea:
        idfea.remove(AuthUserKey)
    return idfea
  appObj.objectStore.updateJSONObject(appObj,"AuthsForEachPerson", personGUID, upd)

  DeleteAuthRecord(appObj, AuthUserKey)
  
def _getAuthInfoForKeyForPersonObj(appObj, authKey):
  authRecordDict, objVer, creationDateTime, lastUpdateDateTime = getAuthRecord(appObj, authKey)
  return {
    "AuthUserKey": authRecordDict["AuthUserKey"],
    "AuthProviderType": authRecordDict["AuthProviderType"],  
    "AuthProviderGUID": authRecordDict["AuthProviderGUID"],
    "tenantName": authRecordDict["tenantName"]
  }
  
def CreatePersonObjFromUserDict(appObj, PersonDict, objVersion, creationDateTime, lastUpdateDateTime):
  AssociatedUserIDs = getListOfUserIDsForPersonNoTenantCheck(appObj, PersonDict['guid'])
  ##print("AAA:", AssociatedUserIDs, ":", personGUID)
  AssociatedUserObjs = []
  for uid in AssociatedUserIDs:
    AssociatedUserObjs.append(GetUser(appObj,uid))
  
  authKeyDICT, objVer2, creationDateTime2, lastUpdateDateTime2 = appObj.objectStore.getObjectJSON(appObj,"AuthsForEachPerson", PersonDict['guid'])
  authObjs = []
  if authKeyDICT is not None:
    #there are people with no auths
    for authKey in authKeyDICT:
      authObjs.append(_getAuthInfoForKeyForPersonObj(appObj, authKey))
  
  personObj = personClass(PersonDict, objVersion, creationDateTime, lastUpdateDateTime, AssociatedUserObjs, authObjs)
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
    
  def updPerson(person, transactionContext):
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
      DeleteAuthRecord(appObj, authKey)
  return personObj
  
def GetPaginatedPersonData(appObj, request, outputFN):
  return appObj.objectStore.getPaginatedResult(appObj, "Persons",  appObj.getPaginatedParamValues(request), request, outputFN)

