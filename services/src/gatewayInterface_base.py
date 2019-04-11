# defines the baseclass for all gateway interfaces



class gatewayInterfaceBaseClass():
  typeName = None
  def __init__(self, config):
    self._setup(config)

  def _setup(self, config):
    raise Exception('Not Overridden')

  def CheckUserInitAndReturnJWTSecretAndKey(self, UserID):
    return self._CheckUserInitAndReturnJWTSecretAndKey(UserID)
  
  def _CheckUserInitAndReturnJWTSecretAndKey(self, UserID):
    raise Exception('Not Overridden')

  def ShouldJWTTokensBeVerified(self):
    return self._ShouldJWTTokensBeVerified

  def _ShouldJWTTokensBeVerified(self):
    raise Exception('Not Overridden')

  def GetJWTTokenSecret(self, UserID):
    return self._GetJWTTokenSecret(UserID)

  def _GetJWTTokenSecret(self, UserID):
    raise Exception('_GetJWTTokenSecret Not Overridden')
