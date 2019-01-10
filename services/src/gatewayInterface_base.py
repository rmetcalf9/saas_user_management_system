# defines the baseclass for all gateway interfaces



class gatewayInterfaceBaseClass():
  typeName = None
  def __init__(self, typeName, config):
    self.typeName =  typeName
    self._setup(config)

  def _setup(self, config):
    raise Exception('Not Overridden')

  def CheckUserInitAndReturnJWTSecretAndKey(self, userDict):
    return self._CheckUserInitAndReturnJWTSecretAndKey(userDict)
  
  def _CheckUserInitAndReturnJWTSecretAndKey(self, userDict):
    raise Exception('Not Overridden')
