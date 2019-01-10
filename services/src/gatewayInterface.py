#Factory methods for gateway interface
import json

from baseapp_for_restapi_backend_with_swagger import readFromEnviroment
from gatewayInterface_none import gatewayInterfaceClass as gi_none
from gatewayInterface_kong import gatewayInterfaceClass as gi_kong
from constants import customExceptionClass

InvalidGatewayInterfaceTypeSpecifiedException = customExceptionClass('APIAPP_GATEWAYINTERFACETYPE value is not recognised')

def getGatewayInterface(env):
  gatewayInterfaceType = readFromEnviroment(env, 'APIAPP_GATEWAYINTERFACETYPE', 'none', None)
  gatewayInterfaceTypeConfigJSON = readFromEnviroment(env, 'APIAPP_GATEWAYINTERFACECONFIG', '{}', None)
  gatewayInterfaceTypeConfigDict = json.loads(gatewayInterfaceTypeConfigJSON)
  
  if gatewayInterfaceType == 'none':
    return gi_none('none',gatewayInterfaceTypeConfigDict)
  if gatewayInterfaceType == 'kong':
    return gi_none('kong',gatewayInterfaceTypeConfigDict)
  raise InvalidGatewayInterfaceTypeSpecifiedException

