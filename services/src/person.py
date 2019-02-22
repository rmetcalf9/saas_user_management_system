#Code for representing a person
# A person can have one or many Auths
# A person has access to many identities
import uuid
from personObj import personClass

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

def getPerson(appObj, personGUID):
  personDICT, objVer = appObj.objectStore.getObjectJSON(appObj,"Persons", personGUID)
  personObj = personClass(personDICT, objVer)
  return personObj

def deletePerson(appObj, personGUID):
  #no object version check
  appObj.objectStore.removeJSONObject(appObj, "Persons", personGUID)
  
  authsForThisGUID, objVer = appObj.objectStore.getObjectJSON(appObj,"AuthsForEachPerson", personGUID)

  appObj.objectStore.removeJSONObject(appObj, "AuthsForEachPerson", personGUID)
  
  for authKey in authsForThisGUID:
    return appObj.objectStore.removeJSONObject(appObj, "userAuths", authKey)
  
  