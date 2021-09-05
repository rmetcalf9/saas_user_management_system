#Code for representing a person
# A person can have one or many Auths
# A person has access to many identities
import uuid
from personObj import personClass
from constants import customExceptionClass
from object_store_abstraction import WrongObjectVersionExceptionClass
from userPersonCommon import RemoveUserAssociation, getListOfUserIDsForPersonNoTenantCheck, GetUser, personDosentExistException
from AuthProviders.authsCommon import getAuthRecord, DeleteAuthRecord

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

def deleteAuthAndUnassiciateFromPerson(appObj, personGUID, AuthUserKey, storeConnection):
  def upd(idfea, transactionContext):
    if idfea is not None:
      if AuthUserKey in idfea:
        idfea.remove(AuthUserKey)
    return idfea
  storeConnection.updateJSONObject("AuthsForEachPerson", personGUID, upd)

  DeleteAuthRecord(appObj, AuthUserKey, storeConnection)

def _getAuthInfoForKeyForPersonObj(appObj, authKey, storeConnection):
  authRecordDict, objVer, creationDateTime, lastUpdateDateTime = getAuthRecord(appObj, authKey, storeConnection)
  return {
    "AuthUserKey": authRecordDict["AuthUserKey"],
    "known_as": authRecordDict["known_as"],
    "AuthProviderType": authRecordDict["AuthProviderType"],
    "AuthProviderGUID": authRecordDict["AuthProviderGUID"],
    "tenantName": authRecordDict["tenantName"]
  }

def CreatePersonObjFromUserDict(appObj, PersonDict, objVersion, creationDateTime, lastUpdateDateTime, storeConnection):
  AssociatedUserIDs = getListOfUserIDsForPersonNoTenantCheck(appObj, PersonDict['guid'], storeConnection)
  ##print("AAA:", AssociatedUserIDs, ":", personGUID)
  AssociatedUserObjs = []
  for uid in AssociatedUserIDs:
    AssociatedUserObjs.append(GetUser(appObj,uid, storeConnection))

  authKeyDICT, objVer2, creationDateTime2, lastUpdateDateTime2, _ = storeConnection.getObjectJSON("AuthsForEachPerson", PersonDict['guid'])
  authObjs = []
  if authKeyDICT is not None:
    #there are people with no auths
    for authKey in authKeyDICT:
      authObjs.append(_getAuthInfoForKeyForPersonObj(appObj, authKey, storeConnection))

  personObj = personClass(PersonDict, objVersion, creationDateTime, lastUpdateDateTime, AssociatedUserObjs, authObjs)
  return personObj

def GetPerson(appObj, personGUID, storeConnection):
  personDICT, objVer, creationDateTime, lastUpdateDateTime, _ = storeConnection.getObjectJSON("Persons", personGUID)
  if personDICT is None:
    return None
  return CreatePersonObjFromUserDict(appObj, personDICT, objVer, creationDateTime, lastUpdateDateTime, storeConnection)

def UpdatePerson(appObj, personGUID, objectVersion, storeConnection):
  #Can't currently update any person data but API added because we will in future
  personObj = GetPerson(appObj, personGUID, storeConnection)
  if personObj is None:
    raise personDosentExistException
  if str(personObj.getObjectVersion()) != str(objectVersion):
    raise WrongObjectVersionExceptionClass

  def updPerson(person, storeConnection):
    if person is None:
      raise personDosentExistException
    return person
  storeConnection.updateJSONObject("Persons", personGUID, updPerson, objectVersion)

  pObj = GetPerson(appObj, personGUID, storeConnection)
  return pObj

#objectVersion used to default to None
def DeletePerson(appObj, personGUID, objectVersion, storeConnection, a,b,c):
  userIDsThisPerson = getListOfUserIDsForPersonNoTenantCheck(appObj, personGUID, storeConnection)
  for userID in userIDsThisPerson:
    RemoveUserAssociation(appObj, userID, personGUID, None, storeConnection)

  #may not have object version check (cascades don't)
  #not cascading delete down to users
  personObj = GetPerson(appObj, personGUID, storeConnection)
  if personObj is None:
    raise personDosentExistException

  storeConnection.removeJSONObject("Persons", personGUID, objectVersion)

  authsForThisGUID, objVer, creationDateTime, lastUpdateDateTime, _ = storeConnection.getObjectJSON("AuthsForEachPerson", personGUID)

  storeConnection.removeJSONObject("AuthsForEachPerson", personGUID, ignoreMissingObject=True)

  storeConnection.removeJSONObject("UsersForEachPerson", personGUID, None, ignoreMissingObject=True)


  if authsForThisGUID is not None:
    for authKey in authsForThisGUID:
      DeleteAuthRecord(appObj, authKey, storeConnection)
  return personObj

def GetPaginatedPersonData(appObj, paginatedParamValues, outputFN, storeConnection):
  return storeConnection.getPaginatedResult("Persons",  paginatedParamValues, outputFN)
