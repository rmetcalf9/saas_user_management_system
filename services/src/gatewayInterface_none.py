from gatewayInterface_base import gatewayInterfaceBaseClass as base
import random
import string
from base64 import b64encode

class gatewayInterfaceClass(base):
  jwtSecret = None
  def _setup(self, config):
    if 'jwtSecret' not in config:
      print('No gateway configured - using None gateway and random JWT secret')
      random_secret_str = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(32))
      self.jwtSecret = b64encode(random_secret_str.encode("utf-8"))
    else:
      print('No gateway configured - using None gateway and config supplied constant JWTSecret')
      self.jwtSecret = config['jwtSecret']

  def _CheckUserInitAndReturnJWTSecretAndKey(self, UserID):
    return { 'key': UserID, 'secret': self.jwtSecret }
    
  def _ShouldJWTTokensBeVerified(self):
    return True

  def _GetJWTTokenSecret(self, UserID):
    return self.jwtSecret
