import TestHelperSuperClass
from ticketManager import ticketManagerClass
from appObj import appObj
import object_store_abstraction

validTicketTypeDict = {
  "tenantName": "todo_xx",
  "ticketTypeName": "TestTicketType001",
  "description": "Created by unittest",
  "enabled": True,
  "welcomeMessage": {
    "agreementRequired": False,
    "title": "Test Ticket Type Welcome Message Title",
    "body": "Test Ticket Type Welcome Message Body",
    "okButtonText": "ok button text"
  },
  "allowUserCreation": True,
  "issueDuration": "123",
  "roles": [ "role1", "secondRole" ],
  "postUseURL": "http:dsadsd",
  "postInvalidURL": "http:dsadsd"
}

class helper(TestHelperSuperClass.testHelperAPIClient):
  def createTicketTypeFromDict(self, sampleTypeObj):
    def fn(storeConnection):
      ticketManager = ticketManagerClass()
      return ticketManager.upsertTicketType(ticketTypeDict=sampleTypeObj, objectVersion=None, storeConnection=storeConnection)
    return appObj.objectStore.executeInsideTransaction(fn)

@TestHelperSuperClass.wipd
class corsPreflight_helpers(helper):
  def test_createTicketTypeWithEmptyDictThowsValidationException(self):
    with self.assertRaises(Exception) as context:
      self.createTicketTypeFromDict({})
    self.checkGotRightExceptionType(context, object_store_abstraction.RepositoryValidationException)

  def test_createTicketTypeWithValidDict(self):
    self.createTicketTypeFromDict(validTicketTypeDict)

  def test_createTicketTypeWithInvalidTenantName(self):
    invalidTickertTypeDict = copy.deepcopt(validTicketTypeDict)
    invalidTickertTypeDict["tenantName"] = "InvalidTenantName"
    with self.assertRaises(Exception) as context:
      self.createTicketTypeFromDict(invalidTickertTypeDict)
    # TODO Work out which exception I want
    self.checkGotRightExceptionType(context, object_store_abstraction.RepositoryValidationException)

