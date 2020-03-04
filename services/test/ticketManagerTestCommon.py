import constants

validTicketTypeDict = {
  "tenantName": constants.masterTenantName,
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
  "issueDuration": 123,
  "roles": [ "role1", "secondRole" ],
  "postUseURL": "http:dsadsd",
  "postInvalidURL": "http:dsadsd"
}
