# Description of Tenant Object

#designed as immutable object
class tenantClass():
  _mainDict = None
  def __init__(self, JSONRetrievedFromStore):
    self._mainDict = JSONRetrievedFromStore.copy()
  
  def getJSONRepresenation(self):
    return self._mainDict

  def getAuthProvider(self, guid):
    if guid not in self._mainDict["AuthProviders"]:
      raise authProviderNotFoundException
    return self._mainDict["AuthProviders"][guid]

  def getNumberOfAuthProviders(self):
    return len(self._mainDict["AuthProviders"])
  
  def getAuthProviderGUIDList(self):
    return self._mainDict["AuthProviders"].keys()

