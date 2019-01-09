# Description of Identity Object
import uuid
from constants import uniqueKeyCombinator

IdentityNotFoundException = Exception('Identity Not Found')
IdentityAlreadyHasThisAuthException = Exception('Identity Already Has This Auth')
IdentityAlreadyHasThisUserException = Exception('Identity Already Has This User')

def createNewIdentity(appObj, name, description, userID):
  guid = str(uuid.uuid4())
  auths = []
  name = name
  description = description
  
  identityDict = {
    'guid': guid,
    'name': name,
    'description': description,
    'userID': userID
  }
  appObj.objectStore.saveJSONObject(appObj, "Identities", guid, identityDict)
#  _associate(appObj, userID, AuthUserKey, guid)
  return identityDict
  
def associateIdentityWithPerson(appObj, personGUID, AuthUserKey):
  def upd(idfea):
    if idfea is None:
      idfea = []
    if personGUID in idfea:
      raise IdentityAlreadyHasThisAuthException
    idfea.append(personGUID)
    return idfea
  appObj.objectStore.updateJSONObject(appObj,"IdentitiesForEachPerson", AuthUserKey, upd)

def getIdentityDict(appObj, personGUID):
  return appObj.objectStore.getObjectJSON(appObj,"Identities", personGUID)

def getListOfIdentitiesForPerson(appObj, personGUID):
  res = {}
  identitiesThisPerson = appObj.objectStore.getObjectJSON(appObj,"IdentitiesForEachPerson", personGUID)
  if identitiesThisPerson is None:
    return {}
  for ite in identitiesThisPerson:
    res[ite] = getIdentityDict(appObj,ite)
  return res

