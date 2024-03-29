#Base class for all authProviders
# An auth has mutiple identities
#  an identity has one user
import constants
import uuid
from .authsCommon import getAuthRecord, SaveAuthRecord, UpdateAuthRecord, DeleteAuthRecord
from .Exceptions import CustomAuthProviderExceptionClass, AuthNotFoundException

InvalidAuthConfigException = CustomAuthProviderExceptionClass('Invalid Auth Config', 'InvalidAuthConfigException')
InvalidAuthCredentialsException = CustomAuthProviderExceptionClass('Invalid Auth Credentials', 'InvalidAuthCredentialsException')
MissingAuthCredentialsException = CustomAuthProviderExceptionClass('Missing Credentials', 'MissingAuthCredentialsException')
tryingToCreateDuplicateAuthException = CustomAuthProviderExceptionClass('That username is already in use', 'tryingToCreateDuplicateAuthException')
InvalidOperationException = CustomAuthProviderExceptionClass('Invalid Operation', 'InvalidOperationException')
NotOverriddenException = Exception('Not Overridden')
ExternalAuthProviderNotReachableException = CustomAuthProviderExceptionClass('ExternalAuthProviderNotReachable', 'ExternalAuthProviderNotReachableException')

#person.py also uses userAuths

#Auth provider objects are created on demand by each request
# for the google auth this means it will read it's file every time
# a static data object is kept for each authProvider (stored via guid)
# to allow for data to be kept between calls
class staticDataClass():
  data = {}
  def resetStaticData(self):
    self.data.clear()
staticDataClassInstance = staticDataClass()
def resetStaticData():
  staticDataClassInstance.resetStaticData()

class authProvider():
  dataDict = None #See checks in init
  guid = None
  tenantName = None
  operationFunctions = None
  tenantObj = None
  appObj = None
  def __init__(self, dataDict, guid, tenantName, tenantObj, appObj, typeSupportsUserCreation = True):
    self.appObj = appObj
    self.tenantObj = tenantObj
    self.operationFunctions = dict()
    if not 'ConfigJSON' in dataDict:
      raise Exception("ERROR No ConfigJSON supplied when creating authProvider")
    if not 'Type' in dataDict:
      raise Exception("ERROR No Type supplied when creating authProvider")
    if not 'AllowUserCreation' in dataDict:
      dataDict['AllowUserCreation'] = False
    if not 'AllowLink' in dataDict:
      dataDict['AllowLink'] = False
    if not 'AllowUnlink' in dataDict:
      dataDict['AllowUnlink'] = False
    if not 'LinkText' in dataDict:
      dataDict['LinkText'] = 'Unlink ' + dataDict['Type']
    #salt not provided during delete operaiton
    #if not 'saltForPasswordHashing' in dataDict:
    #  raise Exception("ERROR No saltForPasswordHashing")

    if not typeSupportsUserCreation:
      if dataDict['AllowUserCreation']:
        raise services.src.constants.customExceptionClass("ERROR auth type " + dataDict['Type'] + " dosen't support user creation", 'InvalidAuthConfigException')

    ##type check
    #if type(dataDict["saltForPasswordHashing"]) is not str:
    #  print('dataDict["saltForPasswordHashing"]:',dataDict["saltForPasswordHashing"])
    #  raise Exception("Auth Provider salt invalid - bad data from object store")
    self.dataDict = dataDict
    self._authSpercificInit()
    self.guid = guid
    self.tenantName = tenantName

  def getStaticData(self):
    #print('getStaticData for:', self.guid)
    if self.guid not in staticDataClassInstance.data:
      return {}
    return staticDataClassInstance.data[self.guid]
  def setStaticData(self, dataValue):
    staticDataClassInstance.data[self.guid] = dataValue
  def hasStaticData(self):
    #print('Checking has static data for:', self.guid)
    #print('staticDataClassInstance.data:',staticDataClassInstance.data)
    return self.guid in staticDataClassInstance.data

  def getType(self):
    return self.dataDict['Type']
  def getConfig(self):
    return self.dataDict['ConfigJSON']
  def getAllowUserCreation(self):
    return self.dataDict['AllowUserCreation']
  def getAllowLink(self):
    return self.dataDict['AllowLink']
  def getAllowUnlink(self):
    return self.dataDict['AllowUnlink']
  def getLinkText(self):
    return self.dataDict['LinkText']
  def getPublicStaticDataDict(self):
    return {}
  def getSaltUsedForPasswordHashing(self):
    return self.dataDict['saltForPasswordHashing']

  #Return the unique identifier for a particular auth
  def _makeKey(self, credentialDICT):
    raise NotOverriddenException

  def _AddAuthForIdentity(self, credentialDICT):
    raise NotOverriddenException

  #check the auth and if it is not valid raise authFailedException
  def _auth(self, appObj, obj, credentialDICT):
    raise NotOverriddenException

  def _authSpercificInit(self):
    raise NotOverriddenException

  #Saved with the authProvs record
  def _getAuthData(self, appObj, credentialDICT):
    raise NotOverriddenException

  def AddAuth(self, appObj, credentialDICT, personGUID, storeConnection, associatePersonWithAuthCalledWhenAuthIsCreated):
    key = self._makeKey(credentialDICT)
    obj, objVer, creationDateTime, lastUpdateDateTime = getAuthRecord(appObj, key, storeConnection)
    if obj is not None:
      #print('key:', key)
      raise tryingToCreateDuplicateAuthException

    mainObjToStore = {
      "AuthUserKey": key,
      "known_as": self.getDefaultKnownAs(credentialDICT),
      "AuthProviderType": self.dataDict["Type"],
      "AuthProviderGUID": self.guid,
      "AuthProviderJSON": self._getAuthData(appObj, credentialDICT),
      "personGUID": personGUID,
      "tenantName": self.tenantName
    }
    SaveAuthRecord(appObj, key, mainObjToStore, storeConnection)
    associatePersonWithAuthCalledWhenAuthIsCreated(appObj, personGUID, key, storeConnection)
    return mainObjToStore

  def AuthReturnAll(self, appObj, credentialDICT, storeConnection, supressAutocreate, authTPL, authTPLQueried, ticketObj, ticketTypeObj):
    #auth TPL will be (obj, objVer, creationDateTime, lastUpdateDateTime)
    if not authTPLQueried:
      authTPL = getAuthRecord(appObj, self._makeKey(credentialDICT), storeConnection)
      authTPLQueried = True
    if authTPL[0] is None:
      if supressAutocreate:
        raise constants.authNotFoundException
      self._AuthActionToTakeWhenThereIsNoRecord(credentialDICT, storeConnection, ticketObj, ticketTypeObj)
      #Assuming action results in an auth record
      authTPL = getAuthRecord(appObj, self._makeKey(credentialDICT), storeConnection)
      if authTPL[0] is None:
        #Still no auth record so return failure
        raise constants.authNotFoundException
    self._auth(appObj, authTPL[0], credentialDICT)
    return authTPL

  def _AuthActionToTakeWhenThereIsNoRecord(self, credentialDICT, storeConnection, ticketObj, ticketTypeObj):
    raise AuthNotFoundException()

  def ValaditeExternalCredentialsAndEnrichCredentialDictForAuth(self, credentialDICT, appObj):
    return self._enrichCredentialDictForAuth(credentialDICT, appObj)

  def Auth(self, appObj, credentialDICT, storeConnection, supressAutocreate, ticketObj, ticketTypeObj):
    authTPL = None
    authTPLQueried = False
    if self.canMakeKeyWithoutEnrichment():
      authTPL = getAuthRecord(appObj, self._makeKey(credentialDICT), storeConnection)
      authTPLQueried = True
    enrichedCredentialDICT = credentialDICT
    #If we can't create users then supress external validation unless we have an auth
    supressEnrich = False
    if authTPLQueried:
      if authTPL[0] is None:
        ticketAllowsUserCreation = False
        if ticketTypeObj is not None:
          ticketAllowsUserCreation = ticketTypeObj.getAllowUserCreation()
        if not ticketAllowsUserCreation: #ticket object trumphs tenant and authprov
          if not self.getAllowUserCreation():
            supressEnrich = True
          if not self.tenantObj.getAllowUserCreation():
            supressEnrich = True
    if not supressEnrich:
      enrichedCredentialDICT = self.ValaditeExternalCredentialsAndEnrichCredentialDictForAuth(credentialDICT, appObj)
    obj, objVer, creationDateTime, lastUpdateDateTime = self.AuthReturnAll(
      appObj, enrichedCredentialDICT, storeConnection, supressAutocreate,
      authTPL=authTPL, authTPLQueried=authTPLQueried,
      ticketObj=ticketObj, ticketTypeObj=ticketTypeObj
    )
    return obj

  # Normally overridden
  def _getTypicalAuthData(self, credentialDICT):
    return {
      "user_unique_identifier": str(uuid.uuid4()), #used for username - needs to be unique across all auth provs
      "known_as": self.getDefaultKnownAs(credentialDICT), #used to display in UI for the user name
      "other_data": {} #Other data like name full name that can be provided - will vary between auth providers
    }

  #Passed in call to createUser when user is first created
  def getTypicalAuthData(self, credentialDICT):
    return self._getTypicalAuthData(credentialDICT)

  # Normally overridden
  def _getDefaultKnownAs(self, credentialDICT):
    return 'autoCreatedUser'

  def getDefaultKnownAs(self, credentialDICT):
    return self._getDefaultKnownAs(credentialDICT)

  def executeAuthOperation(self, appObj, credentialDICT, storeConnection, operationName, operationDICT, ticketObj, ticketTypeObj):
    #for processing operations that change the auth record. This requires existing credentials.
    # one example of an auth operaiton is 'resetpassword' for the internal ath

    if operationName not in self.operationFunctions:
      raise InvalidOperationException

    #Get the auth object - this will raise an exception is the credentials are wrong
    ##Problem to do the auth we need to know the username
    ## but it is not a field in the JWT token
    ## IT is in the response to currentAuthInfo so the webapp can retrieve it from there and supply it correctly in credentials
    authObj, objectVersion, creationDateTime, lastUpdateDateTime = self.AuthReturnAll(
      appObj, credentialDICT, storeConnection, False,
      authTPL=None, authTPLQueried=False,
      ticketObj=ticketObj, ticketTypeObj=ticketTypeObj
    )
    for x in self.operationFunctions[operationName]['requiredDictElements']:
      if x not in operationDICT:
        raise customExceptionClass('Missing operation paramater - ' + x,'OperationParamMissingException')
    (resultValue, alteredAuthObj) = self.operationFunctions[operationName]['fn'](appObj, authObj, storeConnection, operationName, operationDICT)

    #Save changed auth data back to object store
    UpdateAuthRecord(appObj, self._makeKey(credentialDICT), alteredAuthObj, objectVersion, storeConnection)

    return resultValue

  #some auth types will need credentials enriched
  ## e.g. for google Auth we recieve a Code, we will need to enrich that to get
  ## a refresh token, access token and a key
  ## This will raise authFailedException if the credentials are invalid (hence can't be enriched)
  def _enrichCredentialDictForAuth(self, credentialDICT, appObj):
    return credentialDICT

  #Overidden for auth provider types that require a seperate call to the register function to create a user
  def requireRegisterCallToAutocreateUser(self):
    return False

  #Can this auth provider generate a key without enriching the credentials?
  #  google cna't becaue we only get a token to authenticate. we need to call the
  #   enrichment process before we can make a unique key and look up local auth record
  def canMakeKeyWithoutEnrichment(self):
    return True
