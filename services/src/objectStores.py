from baseapp_for_restapi_backend_with_swagger import readFromEnviroment
import json
from constants import customExceptionClass

from objectStores_Memory import ObjectStore_Memory
from objectStores_SQLAlchemy import ObjectStore_SQLAlchemy

InvalidObjectStoreConfigInvalidJSONException = customExceptionClass('APIAPP_OBJECTSTORECONFIG value is not valid JSON')
InvalidObjectStoreConfigMissingTypeException = customExceptionClass('APIAPP_OBJECTSTORECONFIG value has no Type attribute')
InvalidObjectStoreConfigUnknownTypeException = customExceptionClass('APIAPP_OBJECTSTORECONFIG Type value is not recognised')

def _createObjectStoreInstanceTypeSpecified(appObj, type, configDICT, initFN):
  print("Using Object Store Type: " + type)
  return initFN(configDICT)

#Based on applicaiton options create an instance of objectStore to be used
def createObjectStoreInstance(appObj, env):
  objectStoreConfigJSON = readFromEnviroment(env, 'APIAPP_OBJECTSTORECONFIG', '{}', None)
  objectStoreConfigDict = None
  try:
    objectStoreConfigDict = json.loads(objectStoreConfigJSON)
  except Exception as err:
    print(err) # for the repr
    print(str(err)) # for just the message
    print(err.args) # the arguments that the exception has been called with. 
    raise(InvalidObjectStoreConfigInvalidJSONException)
  
  if (objectStoreConfigJSON == '{}'):
    objectStoreConfigDict["Type"] = "Memory"

  if "Type" not in objectStoreConfigDict:
    raise InvalidObjectStoreConfigMissingTypeException
  if objectStoreConfigDict["Type"] == "Memory":
    return _createObjectStoreInstanceTypeSpecified(appObj, "Memory", objectStoreConfigDict, ObjectStore_Memory)
  if objectStoreConfigDict["Type"] == "SQLAlchemy":
    return _createObjectStoreInstanceTypeSpecified(appObj, "SQLAlchemy", objectStoreConfigDict, ObjectStore_SQLAlchemy)

  raise InvalidObjectStoreConfigUnknownTypeException

