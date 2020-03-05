# Ticketing system

See [Process Diagram](https://linkthethings.com/#/linkvis/charts/a3a86a2c-03ed-4e01-bc5c-d4ba4b57c213?v=560bb2da-e2f2-483b-bb3c-2f0be20b0cf3)

Process:

 - Add Ticket for user
 - User visits ticker url

If not expired
 - User logs in
 - User new account has roles added

If expired
 - User can request for renew

If used
 - User message displayed

# Ticket Data

## Ticket Type

```
{
  id: GUID for ticket Type
  tenantName: tenant this ticket is valid for
  ticketTypeName: for admin screens
  description: for admin screens
  enabled: boolean 
  welcomeMessage: {
    agreementRequired: boolean
    title: 'a',
    body: 'b',
    okButtonText: 'Ok'
  },
  allowUserCreation: boolean,
  issueDuration: hours to issue ticket for on creation
  roles: [
    name: name of role to give to user
  ],
  postUseURL: url to send user to after ticket is used
  postInvalidURL: url to send user to after invalid or request validaiton
}
```
Validation - hasaccount role is not allowed

### Operations
 - ADMIN Create
 - ADMIN Edit (Covers disable, add role etc.)
 - ADMIN Delete

## Ticket

I need a bulk method of creating tickets which will accept a list of foreign keys and output a list of urls.

```
 {
   id: Unique GUID user for verification
   typeGUID: link to Ticket Type
   expiry: Expiry date
   externalKey: Any text to link to foreign data e.g. from mail list
   usedDate: Date the invite was used or None
   useWithUserID: GUID of user that used ticket
   reactivationRequested: Date reactivation was requested or None
   reactivatedTicketID: ID of reactivated ticket
   disabled: Allow to disable single key without whole type. Not possible to re-enable - instead new key must be issued
 }

type: Extra field in query - this is all the fileds in ticket type model including metadata!
isUsable: Extra field in query - returns isUsable information
```

externalKey - This must be unique per ticket type, so I can look up if I know both External Key and Ticker Type GUID.

### Operations:
 - ADMIN CreateBatch
  - accepts a list of externalKeys
  - sets id, typeId, expiry and externalKey
  - must check for uniqueness of typeGUID | externalKey
  - Returns report with created and errored external keys
 - ADMIN Disable - sets disabled (one way)
 - ADMIN Reactivate - sets reactivatedTicketID
 - ADMIN Get Paginated list - gets list of tickets of a particular type for admin screens

NO Admin Delete operation - tickets are only deleted when the ticket type is deleted. They can be deactivated instead.

 - LOGIN get ticket - retrieves ticket
   - extra field: type - embeded ticket type model
   - extra field: isUsable - checks and returns INVALID, EXPIRED or USABLE
     - ticket type enabled
     - ticket not disabled
     - ticket has not been used
     - expiry date
 - LOGIN RequestReactivation - sets reactivationRequested
 - LOGIN Use - checks "AllowUserCreate" and isUsable then sets usedDate and useWithUserID

### Reposiories needed for ticket:

repositoryTicket
 - key(ticketid)
 - used for whole key data
repositoryTicketTypeTickets
 - key(tickettypeid)
 - List of all forign keys for uniquness check
 - List of all tickets???? 
 
 (Should I split off the last two into seperate repositories?) 
 - Pro - Tickets are given out per type so if I reach a limit of more than a 1000 a short term workaround would be to create duplicate types.
 - Pro - repositoryTicketTypeTickets chnages will be infrequent. Only batch creation and ticket type deletion. We can't delete tickets without deleting the whole type so records will only change when batches are added.
 - Not Concern - Paginated data will be required from the main repository so that is not a concern.
 - Not Concern - Individual tickets are changed in their lifecycle but this happens in main table

Secondary repositoryTicketTypeTickets will only be read from or written to in admin operation CreateBatch so it can handle lifecycle 

