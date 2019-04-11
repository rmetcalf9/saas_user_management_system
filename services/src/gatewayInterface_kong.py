from gatewayInterface_base import gatewayInterfaceBaseClass as base
from constants import customExceptionClass

  #  kongusername = appObj.globalParamObject.LOGINEP_LDAP_CONSUMERCLIENTID_PREFIX + username
  #  appObj.kongObj.ensureUserExistsWithACL(kongusername, ldapResult['Groups'])
  #  jwtToken = appObj.kongObj.getJWTToken(kongusername)

InvalidKongGatewayInterfaceConfigException = customExceptionClass('APIAPP_GATEWAYINTERFACECONFIG value is not valid')


class gatewayInterfaceClass(base):
  jwtSecret = None
  kongISS = None
  def _setup(self, config):
    if 'jwtSecret' not in config:
      raise InvalidKongGatewayInterfaceConfigException
    else:
      print('Kong gateway with static JWTSecret and single consumer')
      self.jwtSecret = config['jwtSecret']

    #Special key for kong to use
    if 'kongISS' not in config:
      print("kongISS missing from APIAPP_GATEWAYINTERFACECONFIG")
      raise InvalidKongGatewayInterfaceConfigException
    else:
      self.kongISS = config['kongISS']

  def _CheckUserInitAndReturnJWTSecretAndKey(self, UserID):
    return { 'key': UserID, 'secret': self.jwtSecret }
    
  def _ShouldJWTTokensBeVerified(self):
    return True

  def _GetJWTTokenSecret(self, UserID):
    return self.jwtSecret

  def enrichJWTClaims(self, JWTDict):
    JWTDict['kong_iss'] = self.kongISS
    return JWTDict
