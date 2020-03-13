from constants import DefaultHasAccountRole, customExceptionClass, objectType_users_associatedPersons
from userObj import userClass

personDosentExistException = customExceptionClass('Person not found', 'personDosentExistException')
userDosentExistException = customExceptionClass('User not found', 'userDosentExistException')

#This file is required to stop circular references between users and persons

def GetUser(appObj, UserID, storeConnection):
  jsonData, objVersion, creationDateTime, lastUpdateDateTime, _ = storeConnection.getObjectJSON("users",UserID)
  if jsonData is None:
    return None
  return CreateUserObjFromUserDict(appObj, jsonData, objVersion, creationDateTime, lastUpdateDateTime, storeConnection)

def CreateUserObjFromUserDict(appObj, UserDict, objVersion, creationDateTime, lastUpdateDateTime, storeConnection):
  userID = UserDict['UserID']
  associatedPersonsList, objVersion2, creationDateTime2, lastUpdateDateTime2, _ = storeConnection.getObjectJSON(objectType_users_associatedPersons,userID)
  return userClass(UserDict, objVersion, creationDateTime, lastUpdateDateTime, associatedPersonsList)



#Called when deleting both a user and a person
# if being called when we are deleting a person then deletePersonFn will not set to None
def RemoveUserAssociation(appObj, userID, personGUID, deletePersonFn, storeConnection):
  ##Remove record from users_associatedPersons
  def updateTheUsersPersonListFn(associatedPersonList, storeConnection):
    if associatedPersonList is None:
      raise userDosentExistException
    if personGUID in associatedPersonList:
      associatedPersonList.remove(personGUID)

    #Removing other reference inside same function so they occur in same transaction
    def updUsersForEachPerson(idfea, storeConnection):
      if idfea is None:
        raise personDosentExistException
      #May not be in list as if person delete is called first, the user delete also calls this
      if userID in idfea:
        idfea.remove(userID)
      return idfea
    storeConnection.updateJSONObject("UsersForEachPerson", personGUID, updUsersForEachPerson)


    return associatedPersonList
  storeConnection.updateJSONObject(objectType_users_associatedPersons, userID, updateTheUsersPersonListFn)


  userListForThisPerson, objectVersion, creationDateTime, lastUpdateDateTime, _ = storeConnection.getObjectJSON("UsersForEachPerson",personGUID)
  if userListForThisPerson is None:
    return

  if deletePersonFn is not None:
    if len(userListForThisPerson)==0:
      #print("RemoveUserAssociation Last user for this persion - deleting the person")
      deletePersonFn(appObj, personGUID, None, storeConnection, 'a','b','c')

def getListOfUserIDsForPersonNoTenantCheck(appObj, personGUID, storeConnection):
  res = []
  userIDsThisPerson, ver, creationDateTime, lastUpdateDateTime, _ = storeConnection.getObjectJSON("UsersForEachPerson", personGUID)
  if userIDsThisPerson is None:
    return []
  return userIDsThisPerson


def getListOfUserIDsForPerson(appObj, personGUID, tenantName, GetUser, storeConnection):
  userIDsThisPerson = getListOfUserIDsForPersonNoTenantCheck(appObj, personGUID, storeConnection)
  userIDsInThisTenant = []
  for curUserID in userIDsThisPerson:
    userObj = GetUser(appObj, curUserID, storeConnection)
    if userObj is None:
      raise Exception("Stored user ID missing")
    if userObj.hasRole(tenantName, DefaultHasAccountRole):
      userIDsInThisTenant.append(curUserID)
  return userIDsInThisTenant
