#Base class for all authProviders


class authProvider():
  authProviderType = None
  configJSON = None
  def __init__(self, authProviderType, configJSON):
    self.authProviderType = authProviderType
    self.configJSON = configJSON

