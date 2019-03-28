from constants import customExceptionClass, DefaultHasAccountRole

from persons import GetPerson, DeletePerson
from userPersonCommon import RemoveUserAssociation, GetUser, userDosentExistException
import copy

#users_associatedPersons 1-1 with user object, seperated out to stop ObjectVersion getting out of sync when it dosen't need to

TryingToCreateDuplicateUserException = customExceptionClass('That username is already in use', 'TryingToCreateDuplicateUserException')
UserAlreadyAssociatedWithThisPersonException = customExceptionClass('User Already Associated With This Person', 'UserAlreadyAssociatedWithThisPersonException')

##Creation functions
## All the functions that sets up the user, roles and asociates the user with a person

def CreateUser(appObj, userData, mainTenant, createdBy, storeConnection):
  #mainTenant is validated by adminAPI
  #print("UpdateUser createdBy:", createdBy)
  UserID = userData['user_unique_identifier']
  KnownAs = userData['known_as']
  OtherData = {}
  if "other_data" in userData:
    OtherData = userData['other_data']
  OtherData["createdBy"] = createdBy
  
  userObj = GetUser(appObj, UserID, storeConnection)
  if userObj is not None:
    raise TryingToCreateDuplicateUserException
  storeConnection.saveJSONObject("users", UserID, {
    "UserID": UserID,
    "TenantRoles": {},
    "known_as": KnownAs,
    "other_data": OtherData
  })
  storeConnection.saveJSONObject("users_associatedPersons", UserID, [])
  if mainTenant is not None:
    AddUserRole(appObj, UserID, mainTenant, DefaultHasAccountRole, storeConnection)

def associateUserWithPerson(appObj, UserID, personGUID, storeConnection):
  #Add reference from User to person
  ## No object version checking because read and update is the same operaiton
  def updUser(user, transactionContext):
    if personGUID not in user:
      user.append(personGUID)
    return user
  storeConnection.updateJSONObject("users_associatedPersons", UserID, updUser)

  def upd(idfea, transactionContext):
    if idfea is None:
      idfea = []
    if UserID in idfea:
      raise UserAlreadyAssociatedWithThisPersonException
    idfea.append(UserID)
    return idfea
  #print('Asociating user ', UserID, ' with ', personGUID)
  
  storeConnection.updateJSONObject("UsersForEachPerson", personGUID, upd)
  
def AddUserRole(appObj, userID, tennantName, roleName, storeConnection):
  def updUser(obj, transactionContext):
    if obj is None:
      raise userDosentExistException
    if tennantName not in obj["TenantRoles"]:
      obj["TenantRoles"][tennantName] = [roleName]
    else:
      obj["TenantRoles"][tennantName].append(roleName)
    return obj
  storeConnection.updateJSONObject("users", userID, updUser)


  
##END OF CREATION FUNCTIONS

def DeleteUser(appObj, UserID, objectVersion, storeConnection):
  userObj = GetUser(appObj, UserID, storeConnection)
  if userObj is None:
    raise userDosentExistException
  associatedPersonList, objVersion, creationDateTime, lastUpdateDateTime = storeConnection.getObjectJSON("users_associatedPersons",UserID)
    
  for personGUID in associatedPersonList:
    RemoveUserAssociation(appObj, UserID, personGUID, DeletePerson, storeConnection)
    
  storeConnection.removeJSONObject("users", UserID, objectVersion)
  storeConnection.removeJSONObject("users_associatedPersons", UserID)
  
  return userObj

def UpdateUser(appObj, UserID,TenantRoles,known_as,other_data, objectVersion, storeConnection):
  userObj = GetUser(appObj, UserID, storeConnection)
  if userObj is None:
    raise userDosentExistException
  if str(userObj.getObjectVersion()) != str(objectVersion):
    raise WrongObjectVersionException

  internalTenantRoles = {}
  for ten in TenantRoles:
    roles = []
    for rol in ten['ThisTenantRoles']:
      roles.append(rol)
    internalTenantRoles[ten['TenantName']] = roles

  jsonForUser = {
    "UserID": UserID,
    "TenantRoles": internalTenantRoles,
    "known_as": known_as,
    "other_data": other_data
  }

  def updUser(user, storeConnection):
    if user is None:
      raise userNotFoundException
    return jsonForUser
  storeConnection.updateJSONObject("users", UserID, updUser, objectVersion)

  uObj = GetUser(appObj, UserID, storeConnection)
  return uObj

def GetPaginatedUserData(appObj, request, outputFN, storeConnection):
  return storeConnection.getPaginatedResult("users",  appObj.getPaginatedParamValues(request), request, outputFN)

def getIdentityDict(appObj, personGUID, storeConnection):
  identifyJSON, objectVer = appObj.objectStore.getObjectJSON(appObj,"Identities", personGUID)
  return identifyJSON

