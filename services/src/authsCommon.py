def getAuthRecord(appObj, key):
  authRecord, objVer, creationDateTime, lastUpdateDateTime = appObj.objectStore.getObjectJSON(appObj,"userAuths", key.upper())
  return authRecord, objVer, creationDateTime, lastUpdateDateTime

def SaveAuthRecord(appObj, key, obj):
  appObj.objectStore.saveJSONObject(appObj,"userAuths",  key.upper(), obj)
  
def DeleteAuthRecord(appObj, key):
  appObj.objectStore.removeJSONObject(appObj, "userAuths", key.upper())