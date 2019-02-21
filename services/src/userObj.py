# Description of Tenant Object
from constants import authProviderNotFoundException
import json
import copy

#designed as immutable object
class userClass():
  _mainDict = None
  _jsonRepersentation = None
  _jsonRepersentationTenantCache = None
  _objectVersion = None
  def __init__(self, JSONRetrievedFromStore, objectVersion):
    self._mainDict = copy.deepcopy(JSONRetrievedFromStore)
    self._objectVersion = objectVersion
    self._jsonRepersentationTenantCache = {}
  
  def _generateJSONRepresenationAndStoreItInCache(self, tenant):
    aa = self._mainDict.copy()
    tenantRolesObj = []
    for a in aa['TenantRoles']:
      if (tenant is None) or (tenant == a):
        tenantRolesObj.append({
          "TenantName": a,
          "ThisTenantRoles": aa['TenantRoles'][a]
        })
    aa["TenantRoles"] = tenantRolesObj
    aa['ObjectVersion'] = self._objectVersion
    
    if tenant is None:
      self._jsonRepersentation = aa
    else:
      self._jsonRepersentationTenantCache[tenant] = aa
  
  #Need to convert authProviders into a list as in _mainDict it is a dict for indexing
  ##If a tenant is passed to this routine only output roles relevant to that tenant
  def getJSONRepresenation(self, tenant = None):
    if tenant is None:
      if self._jsonRepersentation is None:
        self._generateJSONRepresenationAndStoreItInCache(tenant)
      return self._jsonRepersentation
    if tenant not in self._jsonRepersentationTenantCache:
      self._generateJSONRepresenationAndStoreItInCache(tenant)
    return self._jsonRepersentationTenantCache[tenant]

  def getObjectVersion(self):
    return self._objectVersion

  #Callers should not expect to update this
  def getReadOnlyDict(self):
    return self._mainDict
