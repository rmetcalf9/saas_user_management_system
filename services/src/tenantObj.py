# Description of Tenant Object
from constants import authProviderNotFoundException
import json
import copy
from authProviders import authProviderFactory

#designed as immutable object
class tenantClass():
  _mainDict = None
  _jsonRepersentation = None
  _objectVersion = None
  def __init__(self, JSONRetrievedFromStore, objectVersion):
    self._mainDict = copy.deepcopy(JSONRetrievedFromStore)
    self._objectVersion = objectVersion
    
    #print(self._mainDict)
    #raise Exception("STOP CHECK")
  
  #Need to convert authProviders into a list as in _mainDict it is a dict for indexing
  def getJSONRepresenation(self):
    if self._jsonRepersentation is None:
      self._jsonRepersentation = self._mainDict.copy()
      ap = []
      for guid in self._mainDict["AuthProviders"].keys():
        #ConfigJSON is held as a string according to the swaggerAPI
        # so flask restplus won't convert it from a dict to a valid json format
        # so we do it here
        tmp = copy.deepcopy(self.getAuthProvider(guid))
        tmp['ConfigJSON'] = json.dumps(tmp['ConfigJSON'])
        tmp['StaticlyLoadedData'] = authProviderFactory(self.getAuthProvider(guid), guid, self.getName(), self, None).getPublicStaticDataDict()
        ap.append(tmp)
      self._jsonRepersentation['AuthProviders'] = ap
      self._jsonRepersentation['ObjectVersion'] = self._objectVersion
    return self._jsonRepersentation

  def getAuthProvider(self, guid):
    if guid not in self._mainDict["AuthProviders"]:
      raise authProviderNotFoundException
    return self._mainDict["AuthProviders"][guid]

  def getNumberOfAuthProviders(self):
    return len(self._mainDict["AuthProviders"])
  
  def getAuthProviderGUIDList(self):
    return self._mainDict["AuthProviders"].keys()

  def getName(self):
    return self._mainDict["Name"]

  def getAllowUserCreation(self):
    return self._mainDict["AllowUserCreation"]

  def getObjectVersion(self):
    return self._objectVersion

  def getJWTCollecitonAllowedOriginList(self):
    return self._mainDict["JWTCollecitonAllowedOriginList"]

