from constants import customExceptionClass, DefaultHasAccountRole

from userObj import userClass

TryingToCreateDuplicateUserException = customExceptionClass('That username is already in use', 'TryingToCreateDuplicateUserException')
userDosentExistException = customExceptionClass('User not found', 'userDosentExistException')
UserAlreadyAssociatedWithThisPersonException = customExceptionClass('User Already Associated With This Person', 'UserAlreadyAssociatedWithThisPersonException')

##Creation functions
## All the functions that sets up the user, roles and asociates the user with a person

def CreateUser(appObj, userData, mainTenant):
  UserID = userData['user_unique_identifier']
  KnownAs = userData['known_as']
  OtherData = {}
  if "other_data" in userData:
    OtherData = userData['other_data']
    
  userObj = GetUser(appObj, UserID)
  if userObj is not None:
    raise TryingToCreateDuplicateUserException
  appObj.objectStore.saveJSONObject(appObj,"users", UserID, {
    "UserID": UserID,
    "TenantRoles": {},
    "known_as": KnownAs,
    "other_data": OtherData
  })
  AddUserRole(appObj, UserID, mainTenant, DefaultHasAccountRole)

def associateUserWithPerson(appObj, UserID, personGUID):
  def upd(idfea):
    if idfea is None:
      idfea = []
    if UserID in idfea:
      raise UserAlreadyAssociatedWithThisPersonException
    idfea.append(UserID)
    return idfea
  #print('Asociating user ', UserID, ' with ', personGUID)
  appObj.objectStore.updateJSONObject(appObj,"UsersForEachPerson", personGUID, upd)
  
def AddUserRole(appObj, userID, tennantName, roleName):
  def updUser(obj):
    if obj is None:
      raise userDosentExistException
    if tennantName not in obj["TenantRoles"]:
      obj["TenantRoles"][tennantName] = [roleName]
    else:
      obj["TenantRoles"][tennantName].append(roleName)
    return obj
  appObj.objectStore.updateJSONObject(appObj,"users", userID, updUser)


  
##END OF CREATION FUNCTIONS
  
def DeleteUser(appObj, UserID, objectVersion):
  userObj = GetUser(appObj, UserID)
  if userObj is None:
    raise userDosentExistException
  appObj.objectStore.removeJSONObject(appObj, "users", UserID, objectVersion)
  return userObj
  
def GetUser(appObj, UserID):
  jsonData, objVersion = appObj.objectStore.getObjectJSON(appObj,"users",UserID)
  if jsonData is None:
    return None
  return userClass(jsonData, objVersion)

def UpdateUser(appObj, UserID,TenantRoles,known_as,other_data, objectVersion):
  userObj = GetUser(appObj, UserID)
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

  def updUser(user):
    if user is None:
      raise userNotFoundException
    return jsonForUser
  appObj.objectStore.updateJSONObject(appObj,"users", UserID, updUser, objectVersion)

  uObj = GetUser(appObj, UserID)
  return uObj

def GetPaginatedUserData(appObj, request, outputFN, filterFN):
  return appObj.objectStore.getPaginatedResult(appObj, "users",  appObj.getPaginatedParamValues(request), request, outputFN, filterFN)

def getIdentityDict(appObj, personGUID):
  identifyJSON, objectVer = appObj.objectStore.getObjectJSON(appObj,"Identities", personGUID)
  return identifyJSON

def getListOfUserIDsForPerson(appObj, personGUID):
  res = []
  userIDsThisPerson, ver = appObj.objectStore.getObjectJSON(appObj,"UsersForEachPerson", personGUID)
  if userIDsThisPerson is None:
    return []
  return userIDsThisPerson
