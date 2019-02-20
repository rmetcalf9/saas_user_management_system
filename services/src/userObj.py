# Description of Tenant Object
from constants import authProviderNotFoundException
import json
import copy

#designed as immutable object
class userClass():
  _mainDict = None
  _jsonRepersentation = None
  _objectVersion = None
  def __init__(self, JSONRetrievedFromStore, objectVersion):
    self._mainDict = copy.deepcopy(JSONRetrievedFromStore)
    self._objectVersion = objectVersion
  
  #Need to convert authProviders into a list as in _mainDict it is a dict for indexing
  def getJSONRepresenation(self):
    if self._jsonRepersentation is None:
      self._jsonRepersentation = self._mainDict.copy()
      tenantRolesObj = []
      for a in self._jsonRepersentation['TenantRoles']:
        tenantRolesObj.append({
          "TenantName": a,
          "ThisTenantRoles": self._jsonRepersentation['TenantRoles'][a]
        })
        self._jsonRepersentation["TenantRoles"] = tenantRolesObj
    return self._jsonRepersentation

  def getObjectVersion(self):
    return self._objectVersion

  #Callers should not expect to update this
  def getReadOnlyDict(self):
    return self._mainDict
