from gatewayInterface_base import gatewayInterfaceBaseClass as base
import random
import string
from base64 import b64encode

class gatewayInterfaceClass(base):
  jwtSecret = None
  def _setup(self, config):
    print('No gateway configured')
    if 'jwtSecret' not in config:
      random_secret_str = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(32))
      self.jwtSecret = b64encode(random_secret_str.encode("utf-8"))
    else:
      self.jwtSecret = config['jwtSecret']

  def _CheckUserInitAndReturnJWTSecretAndKey(self, userDict):
    return { 'key': 'abc', 'secret': self.jwtSecret }