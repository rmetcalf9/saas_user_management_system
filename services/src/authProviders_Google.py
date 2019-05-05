#Auth provider that links with google login
from authProviders_base import authProvider, InvalidAuthConfigException

class authProviderGoogle(authProvider):
  def __init__(self, dataDict, guid, tenantName):
    super().__init__(dataDict, guid, tenantName)
    #self.operationFunctions['ResetPassword'] = {
    #  'fn': self._executeAuthOperation_resetPassword,
    #  'requiredDictElements': ['newPassword']
    #}

  def _authSpercificInit(self):
    pass
