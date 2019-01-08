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
  
def associateIdentityWithAuth(appObj, identityGUID, AuthUserKey):
  def upd(idfea):
    if idfea is None:
      idfea = []
    if identityGUID in idfea:
      raise IdentityAlreadyHasThisAuthException
    idfea.append(identityGUID)
    return idfea
  appObj.objectStore.updateJSONObject(appObj,"IdentitiesForEachAuth", AuthUserKey, upd)

def getIdentityDict(appObj, identityGUID):
  return appObj.objectStore.getObjectJSON(appObj,"Identities", identityGUID)

def getListOfIdentitiesForAuth(appObj, AuthUserKey):
  res = {}
  for ite in appObj.objectStore.getObjectJSON(appObj,"IdentitiesForEachAuth", AuthUserKey):
    res[ite] = getIdentityDict(appObj,ite)
  return res

