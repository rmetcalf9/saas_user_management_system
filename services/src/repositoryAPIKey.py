from object_store_abstraction import RepositoryBaseClass, RepositoryValidationException
from repositoryAPIKeyObj import factoryFn as APIKeyObjFactoryFn
import constants

class APIKeyRepositoryClass(RepositoryBaseClass):
  appObj = None

  def __init__(self):
    RepositoryBaseClass.__init__(self, "apikeys", APIKeyObjFactoryFn)

  def getAPIKEY(self, apiKey, storeConnection):
    return self.get(apiKey, storeConnection)
