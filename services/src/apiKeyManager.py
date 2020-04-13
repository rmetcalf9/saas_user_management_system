import repositoryAPIKey
import uuid

class apiKeyManagerClass():
  repositoryAPIKey = None

  def __init__(self, appObj):
    self.repositoryAPIKey = repositoryAPIKey.APIKeyRepositoryClass()


  def createAPIKey(self, tenant, decodedJWTToken, restrictedRoles, externalDataDict, storeConnection):
    APIKey = str(uuid.uuid4())
    userID = decodedJWTToken.getUserID()


    APIKeyDict = {
      "id": self.getHashedAPIKey(APIKey=APIKey, userID=userID),
      "tenantName": tenant,
      "createdByUserID": userID,
      "restrictedRoles": restrictedRoles,
      "externalData": externalDataDict
    }

    (objID, objectVersion) = self.repositoryAPIKey.upsert(APIKeyDict, None, storeConnection=storeConnection)

    APIKeyObj = self.repositoryAPIKey.get(objID, storeConnection)

    return (APIKeyObj, APIKey)

  def getHashedAPIKey(self, APIKey, userID):
    return APIKey