def getAuthRecord(appObj, key, storeConnection):
  authRecord, objVer, creationDateTime, lastUpdateDateTime = storeConnection.getObjectJSON("userAuths", key.upper())
  return authRecord, objVer, creationDateTime, lastUpdateDateTime

def SaveAuthRecord(appObj, key, obj, storeConnection):
  storeConnection.saveJSONObject("userAuths",  key.upper(), obj)
  
#only called from person as person auth link needs to be removed
def DeleteAuthRecord(appObj, key, storeConnection):
  storeConnection.removeJSONObject("userAuths", key.upper())