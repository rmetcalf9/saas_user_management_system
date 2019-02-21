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
  
def associateIdentityWithPerson(appObj, identityGUID, personGUID):
  def upd(idfea):
    if idfea is None:
      idfea = []
    if identityGUID in idfea:
      raise IdentityAlreadyHasThisAuthException
    idfea.append(identityGUID)
    return idfea
  appObj.objectStore.updateJSONObject(appObj,"IdentitiesForEachPerson", personGUID, upd)

def getIdentityDict(appObj, personGUID):
  identifyJSON, objectVer = appObj.objectStore.getObjectJSON(appObj,"Identities", personGUID)
  return identifyJSON

def getListOfIdentitiesForPerson(appObj, personGUID):
  res = {}
  identitiesThisPerson, ver = appObj.objectStore.getObjectJSON(appObj,"IdentitiesForEachPerson", personGUID)
  if identitiesThisPerson is None:
    return {}
  for ite in identitiesThisPerson:
    res[ite] = getIdentityDict(appObj,ite)
  return res

