# Description of Tenant Object

#designed as immutable object
class tenantClass():
  _mainDict = None
  _jsonRepersentation = None
  def __init__(self, JSONRetrievedFromStore):
    self._mainDict = JSONRetrievedFromStore.copy()
  
  #Need to convert authPRoviders into a list as in _mainDict it is a dict for indexing
  def getJSONRepresenation(self):
    if self._jsonRepersentation is None:
      self._jsonRepersentation = self._mainDict.copy()
      ap = []
      for guid in self._mainDict["AuthProviders"].keys():
        ap.append(self.getAuthProvider(guid))
      self._jsonRepersentation['AuthProviders'] = ap
    return self._jsonRepersentation

  def getAuthProvider(self, guid):
    if guid not in self._mainDict["AuthProviders"]:
      raise authProviderNotFoundException
    return self._mainDict["AuthProviders"][guid]

  def getNumberOfAuthProviders(self):
    return len(self._mainDict["AuthProviders"])
  
  def getAuthProviderGUIDList(self):
    return self._mainDict["AuthProviders"].keys()

