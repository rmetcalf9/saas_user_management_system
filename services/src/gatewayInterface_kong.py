from gatewayInterface_base import gatewayInterfaceBaseClass as base
from constants import customExceptionClass

  #  kongusername = appObj.globalParamObject.LOGINEP_LDAP_CONSUMERCLIENTID_PREFIX + username
  #  appObj.kongObj.ensureUserExistsWithACL(kongusername, ldapResult['Groups'])
  #  jwtToken = appObj.kongObj.getJWTToken(kongusername)

InvalidKongGatewayInterfaceConfigException = customExceptionClass('APIAPP_GATEWAYINTERFACECONFIG value is not valid')


class gatewayInterfaceClass(base):
  kongISS = None
  def _setup(self, config):
    if 'jwtSecret' in config:
      raise Exception("ERROR jwtSecret should not be in kong gateway options")

    #Special key for kong to use
    if 'kongISS' not in config:
      print("kongISS missing from APIAPP_GATEWAYINTERFACECONFIG")
      raise InvalidKongGatewayInterfaceConfigException
    else:
      self.kongISS = config['kongISS']

  def enrichJWTClaims(self, JWTDict):
    JWTDict['kong_iss'] = self.kongISS
    return JWTDict
