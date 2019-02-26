from constants import DefaultHasAccountRole

#This file is required to stop circular references between users and persons

#Called when deleting both a user and a person
# if being called when we are deleting a person then deletePersonFn will not set to None
def RemoveUserAssociation(appObj, userID, personGUID, deletePersonFn):
  ##REmove record from users_associatedPersons
  def updateTheUsersPersonListFn(associatedPersonList):
    if personGUID in associatedPersonList:
      associatedPersonList.remove(personGUID)
    return associatedPersonList
  appObj.objectStore.updateJSONObject(appObj,"users_associatedPersons", userID, updateTheUsersPersonListFn)
  
  
  def upd(idfea):
    #May not be in list as if person delete is called first, the user delete also calls this
    if userID in idfea:
      idfea.remove(userID)
    return idfea
  appObj.objectStore.updateJSONObject(appObj,"UsersForEachPerson", personGUID, upd)
  #print("RemoveUserAssociation per:user = ",personGUID, ":", userID)
  userListForThisPerson, objectVersion, creationDateTime, lastUpdateDateTime = appObj.objectStore.getObjectJSON(appObj,"UsersForEachPerson",personGUID)
  if userListForThisPerson is None:
    return
    
  if deletePersonFn is not None:
    if len(userListForThisPerson)==0:
      #print("RemoveUserAssociation Last user for this persion - deleting the person")
      deletePersonFn(appObj, personGUID)

def getListOfUserIDsForPersonNoTenantCheck(appObj, personGUID):
  res = []
  userIDsThisPerson, ver, creationDateTime, lastUpdateDateTime = appObj.objectStore.getObjectJSON(appObj,"UsersForEachPerson", personGUID)
  if userIDsThisPerson is None:
    return []
  return userIDsThisPerson

  
def getListOfUserIDsForPerson(appObj, personGUID, tenantName, GetUser):
  userIDsThisPerson = getListOfUserIDsForPersonNoTenantCheck(appObj, personGUID)
  userIDsInThisTenant = []
  for curUserID in userIDsThisPerson:
    userObj = GetUser(appObj,curUserID)
    if userObj is None:
      raise Exception("Stored user ID missing")
    if userObj.hasRole(tenantName, DefaultHasAccountRole):
      userIDsInThisTenant.append(curUserID)
  return userIDsInThisTenant
