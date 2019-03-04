def getAuthRecord(appObj, key):
  authRecord, objVer, creationDateTime, lastUpdateDateTime = appObj.objectStore.getObjectJSON(appObj,"userAuths", key)
  return authRecord, objVer, creationDateTime, lastUpdateDateTime

