#Code for representing a person
# A person can have one or many Auths
# A person has access to many identities
import uuid

def CreatePerson(appObj):
  guid = str(uuid.uuid4())
  personDict = {
    'guid': guid
  }
  appObj.objectStore.saveJSONObject(appObj, "Persons", guid, personDict)
  return personDict

def associatePersonWithAuth(appObj, identityGUID, AuthUserKey):
  def upd(idfea):
    if idfea is None:
      idfea = []
    if identityGUID in idfea:
      raise IdentityAlreadyHasThisAuthException
    idfea.append(identityGUID)
    return idfea
  appObj.objectStore.updateJSONObject(appObj,"PersonsForEachAuth", AuthUserKey, upd)

def getPerson(appObj, personGUID):
  personJSON, objVer = appObj.objectStore.getObjectJSON(appObj,"Persons", personGUID)
  return personJSON
