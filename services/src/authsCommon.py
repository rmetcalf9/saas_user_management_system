def getAuthRecord(appObj, key, storeConnection):
  authRecord, objVer, creationDateTime, lastUpdateDateTime = storeConnection.getObjectJSON("userAuths", key.upper())
  if authRecord is not None:
    if 'known_as' not in authRecord:
      authRecord['known_as'] = str(authRecord['AuthUserKey'])
  return authRecord, objVer, creationDateTime, lastUpdateDateTime

def SaveAuthRecord(appObj, key, obj, storeConnection):
  storeConnection.saveJSONObject("userAuths",  key.upper(), obj)

def UpdateAuthRecord(appObj, key, obj, objectVersion, storeConnection):
  def updFn(idfea, storeConnection):
    return obj
  storeConnection.updateJSONObject("userAuths", key.upper(), updFn, objectVersion)

#only called from person as person auth link needs to be removed
# - Update now called from unlink which deletes auths
def DeleteAuthRecord(appObj, key, storeConnection):
  storeConnection.removeJSONObject("userAuths", key.upper())
