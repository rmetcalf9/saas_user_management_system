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
  tenant: tenant this ticket is valid for
  tenantName: for admin screens
  description: for admin screens
  enabled: boolean 
  welcomeMessage: {
    agreementRequired: boolean
    title: 'a',
    body: 'b'
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
 }
```
### Operations:
 - ADMIN Create - sets id, typeId, expiry and externalKey
 - LOGIN isUsable - checks and returns INVALID, EXPIRED or USABLE
   - ticket type enabled
   - if ticket has been used
   - expiry date
 - LOGIN Use - checks "AllowUserCreate" and isUsable then sets usedDate and useWithUserID
 - ADMIN RequestReactivation - sets reactivationRequested
 - ADMIN Reactivate - sets reactivatedTicketID
 - ADMIN Delete - deletes ticket (works with status of ticket)
