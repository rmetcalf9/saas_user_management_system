from gatewayInterface_base import gatewayInterfaceBaseClass as base
import random
import string
from base64 import b64encode


class gatewayInterfaceClass(base):
  def _setup(self, config):
    if 'jwtSecret' in config:
      raise Exception("Error JWTSecret should not be set in none gateway config")

