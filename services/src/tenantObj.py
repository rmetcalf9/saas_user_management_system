# Description of Tenant Object
import constants
import json
import copy
from AuthProviders import authProviderFactory

#designed as immutable object
class tenantClass():
  _mainDict = None
  _jsonRepersentation = None
  _objectVersion = None
  def __init__(self, JSONRetrievedFromStore, objectVersion, appObj):
    self._mainDict = copy.deepcopy(JSONRetrievedFromStore)

    if not 'JWTCollectionAllowedOriginList' in self._mainDict:
      if self._mainDict['Name'] == constants.masterTenantName:
        self._mainDict['JWTCollectionAllowedOriginList'] = list(map(lambda x: x.strip(), appObj.APIAPP_DEFAULTMASTERTENANTJWTCOLLECTIONALLOWEDORIGINFIELD.split(',')))
      else:
        self._mainDict['JWTCollectionAllowedOriginList'] = []
    for curAuthProv in self._mainDict['AuthProviders']:
      if not 'AllowLink' in self._mainDict['AuthProviders'][curAuthProv]:
        self._mainDict['AuthProviders'][curAuthProv]['AllowLink'] = False
      if not 'AllowUnlink' in self._mainDict['AuthProviders'][curAuthProv]:
        self._mainDict['AuthProviders'][curAuthProv]['AllowUnlink'] = False
      if not 'LinkText' in self._mainDict['AuthProviders'][curAuthProv]:
        self._mainDict['AuthProviders'][curAuthProv]['LinkText'] = 'Link ' + self._mainDict['AuthProviders'][curAuthProv]['Type']

    if not "TicketOverrideURL" in self._mainDict:
      self._mainDict["TicketOverrideURL"] = ""

    if not "TenantBannerHTML" in self._mainDict:
      self._mainDict["TenantBannerHTML"] = ""
    if not "SelectAuthMessage" in self._mainDict:
      self._mainDict["SelectAuthMessage"] = "How do you want to verify who you are?"


    self._objectVersion = objectVersion

    if self._mainDict["JWTCollectionAllowedOriginList"] is None:
      raise Exception("Internal - JWTCollectionAllowedOriginList not defined")

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
      raise constants.authProviderNotFoundException
    return self._mainDict["AuthProviders"][guid]

  def getNumberOfAuthProviders(self):
    return len(self._mainDict["AuthProviders"])

  def getAuthProviderGUIDList(self):
    return self._mainDict["AuthProviders"].keys()

  def getSingleAuthProviderOfType(self, type):
    # return None if there is no auth provider of this type or if there is more
    #  than one
    foundProv = None
    for x in self._mainDict["AuthProviders"]:
      if self._mainDict["AuthProviders"][x]["Type"] == type:
        if foundProv is not None:
          return None
        foundProv = self._mainDict["AuthProviders"][x]
    return foundProv

  def getName(self):
    return self._mainDict["Name"]

  def getAllowUserCreation(self):
    return self._mainDict["AllowUserCreation"]

  def getObjectVersion(self):
    return self._objectVersion

  def getJWTCollectionAllowedOriginList(self):
    return self._mainDict["JWTCollectionAllowedOriginList"]
