import TestHelperSuperClass
from ticketManager import ticketManagerClass
from appObj import appObj

class helper(TestHelperSuperClass.testHelperAPIClient):
  pass

@TestHelperSuperClass.wipd
class corsPreflight_helpers(helper):
  def test_createTicketWithEmptyDictThowsValidationException(self):
    def fn (storeConnection):
      ticketManager = ticketManagerClass()
      ret = None
      with self.assertRaises(Exception) as context:
        ret = ticketManager.upsertTicketType(ticketTypeDict={}, objectVersion=None, storeConnection=storeConnection)
      self.checkGotRightException(context, invalidConfigurationException)
      return ret

    appObj.objectStore.executeInsideTransaction(fn)