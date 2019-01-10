# defines the baseclass for all gateway interfaces



class gatewayInterfaceBaseClass():
  typeName = None
  def __init__(self, typeName, config):
    self.typeName =  typeName
    self._setup(config)

  def _setup(self, config):
    raise Exception('Not Overridden')

  def CheckUserInitAndReturnJWTSecret(self, userDict):
    return self._CheckUserInitAndReturnJWTSecret(userDict)
  
  def _CheckUserInitAndReturnJWTSecret(self, userDict):
    raise Exception('Not Overridden')
