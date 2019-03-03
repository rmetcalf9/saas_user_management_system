from constants import DefaultHasAccountRole, customExceptionClass
from userObj import userClass

personDosentExistException = customExceptionClass('Person not found', 'personDosentExistException')
userDosentExistException = customExceptionClass('User not found', 'userDosentExistException')

#This file is required to stop circular references between users and persons

def GetUser(appObj, UserID):
  jsonData, objVersion, creationDateTime, lastUpdateDateTime = appObj.objectStore.getObjectJSON(appObj,"users",UserID)
  if jsonData is None:
    return None
  return CreateUserObjFromUserDict(appObj, jsonData, objVersion, creationDateTime, lastUpdateDateTime)
  
def CreateUserObjFromUserDict(appObj, UserDict, objVersion, creationDateTime, lastUpdateDateTime):
  associatedPersonsList, objVersion2, creationDateTime2, lastUpdateDateTime2 = appObj.objectStore.getObjectJSON(appObj,"users_associatedPersons",UserDict['UserID'])
  return userClass(UserDict, objVersion, creationDateTime, lastUpdateDateTime, associatedPersonsList)



#Called when deleting both a user and a person
# if being called when we are deleting a person then deletePersonFn will not set to None
def RemoveUserAssociation(appObj, userID, personGUID, deletePersonFn):
  ##Remove record from users_associatedPersons
  def updateTheUsersPersonListFn(associatedPersonList, transactionContext):
    if associatedPersonList is None:
      raise userDosentExistException
    if personGUID in associatedPersonList:
      associatedPersonList.remove(personGUID)

    #Removing other reference inside same function so they occur in same transaction
    def updUsersForEachPerson(idfea, transactionContext):
      if idfea is None:
        raise personDosentExistException
      #May not be in list as if person delete is called first, the user delete also calls this
      if userID in idfea:
        idfea.remove(userID)
      return idfea
    appObj.objectStore.updateJSONObject(appObj,"UsersForEachPerson", personGUID, updUsersForEachPerson, transactionContext)
      
      
    return associatedPersonList
  appObj.objectStore.updateJSONObject(appObj,"users_associatedPersons", userID, updateTheUsersPersonListFn)
  
  
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
