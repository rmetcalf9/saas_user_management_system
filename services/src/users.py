from constants import customExceptionClass, DefaultHasAccountRole

TryingToCreateDuplicateUserException = customExceptionClass('That username is already in use', 'TryingToCreateDuplicateUserException')


def CreateUser(appObj, userData, mainTenant):
  UserID = userData['user_unique_identifier']
  KnownAs = userData['known_as']
  OtherData = {}
  if "other_data" in userData:
    OtherData = userData['other_data']
    
  (user, objVer) = GetUser(appObj, UserID)
  if user is not None:
    raise TryingToCreateDuplicateUserException
  appObj.objectStore.saveJSONObject(appObj,"users", UserID, {
    "UserID": UserID,
    "TenantRoles": {},
    "known_as": KnownAs,
    "other_data": OtherData
  })
  AddUserRole(appObj, UserID, mainTenant, DefaultHasAccountRole)

def GetUser(appObj, UserID):
  return appObj.objectStore.getObjectJSON(appObj,"users",UserID)

def AddUserRole(appObj, userID, tennantName, roleName):
  def updUser(obj):
    if obj is None:
      raise userNotFoundException
    if tennantName not in obj["TenantRoles"]:
      obj["TenantRoles"][tennantName] = [roleName]
    else:
      obj["TenantRoles"][tennantName].append(roleName)
    return obj
  appObj.objectStore.updateJSONObject(appObj,"users", userID, updUser)

def GetPaginatedUserData(appObj, request, outputFN, filterFN):
  return appObj.objectStore.getPaginatedResult(appObj, "users",  appObj.getPaginatedParamValues(request), request, outputFN, filterFN)

