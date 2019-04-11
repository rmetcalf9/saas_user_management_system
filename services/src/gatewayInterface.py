#Factory methods for gateway interface
import json

from baseapp_for_restapi_backend_with_swagger import readFromEnviroment
from gatewayInterface_none import gatewayInterfaceClass as gi_none
from gatewayInterface_kong import gatewayInterfaceClass as gi_kong
from constants import customExceptionClass

InvalidGatewayInterfaceConfigException = customExceptionClass('APIAPP_GATEWAYINTERFACECONFIG value is not valid')
InvalidGatewayInterfaceTypeSpecifiedException = customExceptionClass('APIAPP_GATEWAYINTERFACECONFIG invalid Type')

def getGatewayInterface(env):
  APIAPP_GATEWAYINTERFACETYPE = readFromEnviroment(env, 'APIAPP_GATEWAYINTERFACECONFIG', '{"Type": "none"}', None)
  
  gatewayInterfaceTypeConfigDict = None
  try:
    gatewayInterfaceTypeConfigDict = json.loads(APIAPP_GATEWAYINTERFACETYPE)
  except Exception as err:
    print("APIAPP_GATEWAYINTERFACECONFIG has invalid JSON")
    print(err) # for the repr
    print(str(err)) # for just the message
    print(err.args) # the arguments that the exception has been called with. 
    raise InvalidGatewayInterfaceConfigException

  if "Type" not in gatewayInterfaceTypeConfigDict:
    print("Type element missing")
    raise InvalidGatewayInterfaceConfigException
  
  
  if gatewayInterfaceTypeConfigDict["Type"] == 'none':
    return gi_none(gatewayInterfaceTypeConfigDict)
  if gatewayInterfaceTypeConfigDict["Type"] == 'kong':
    return gi_kong(gatewayInterfaceTypeConfigDict)
    
  print("Gatewat interface type " + gatewayInterfaceTypeConfigDict["Type"] + " not found")
  raise InvalidGatewayInterfaceTypeSpecifiedException

