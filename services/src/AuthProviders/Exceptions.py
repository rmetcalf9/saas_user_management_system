
class CustomAuthProviderExceptionClass(Exception):
  id = None
  text = None
  def __init__(self, text, iid=None):
    if iid is None:
      self.id = text
    else:
      self.id = iid
    self.text = text

class AuthNotFoundException(Exception):
  text = "authNotFoundException"

