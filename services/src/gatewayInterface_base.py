# defines the baseclass for all gateway interfaces



class gatewayInterfaceBaseClass():
  typeName = None
  appObj = None
  def __init__(self, config, appObj):
    self.appObj = appObj
    self._setup(config)

  def _setup(self, config):
    raise Exception('Not Overridden')

  #Passed the dict and adds any extra claims for the gateway
  def enrichJWTClaims(self, JWTDict):
    return JWTDict
