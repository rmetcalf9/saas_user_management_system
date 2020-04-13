import repositoryAPIKey
import uuid
##import bcrypt
from base64 import b64encode
from werkzeug.exceptions import NotFound

class apiKeyManagerClass():
  repositoryAPIKey = None
  appObj = None

  def __init__(self, appObj):
    self.repositoryAPIKey = repositoryAPIKey.APIKeyRepositoryClass()
    self.appObj = appObj

  def createAPIKey(self, tenant, decodedJWTToken, restrictedRoles, externalDataDict, storeConnection):
    APIKey = str(uuid.uuid4())
    userID = decodedJWTToken.getUserID()


    APIKeyDict = {
      "id": self.getHashedAPIKey(APIKey=APIKey),
      "tenantName": tenant,
      "createdByUserID": userID,
      "restrictedRoles": restrictedRoles,
      "externalData": externalDataDict
    }

    (objID, objectVersion) = self.repositoryAPIKey.upsert(APIKeyDict, None, storeConnection=storeConnection)

    APIKeyObj = self.repositoryAPIKey.get(objID, storeConnection)

    return (APIKeyObj, APIKey)

  def getHashedAPIKey(self, APIKey):
    #Using constant salt rather than a generated saly
    # this is nessecary because this needs to be a looked up key in the datatable so no prospect of carrying a salt inline
    # this would allow for a rainbow table style attack on the stored data because the hash is known as long as the attacker
    # also obtains the master password
    salt = b'$2b$12$pXti32TD6.kwYUnLr.1vh.'
    ##return b64encode(bcrypt.hashpw(str.encode(APIKey + "xx" + self.appObj.APIAPP_MASTERPASSWORDFORPASSHASH), salt)).decode('utf-8')
    return b64encode(self.appObj.bcrypt.hashpw(str.encode(APIKey + "xx" + self.appObj.APIAPP_MASTERPASSWORDFORPASSHASH), salt)).decode('utf-8')

  def getAPIKeyDict(
     self,
     decodedJWTToken,
     tenant,
     apiKeyID,
     storeConnection
   ):
    apiKeyObj =  self.repositoryAPIKey.get(apiKeyID, storeConnection)
    if not apiKeyObj.userCanRead(tenantName=tenant, userID=decodedJWTToken.getUserID()):
      raise NotFound
    return apiKeyObj.getDict(), 200

  def getAPIKeyPaginatedResults(self, decodedJWTToken, tenantName, paginatedParamValues, outputFN, storeConnection):
    userID=decodedJWTToken.getUserID()
    def filterFn(obj, whereClauseText):
      return obj.userCanRead(tenantName=tenantName, userID=userID)
    return self.repositoryAPIKey.getPaginatedResult(paginatedParamValues, outputFN, storeConnection, filterFn)