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

 {
   id: Unique GUID user for verification
   expiry: Expiry date
   foreignkey: Any text to link to foreign data
   useddate: Date the invite was used or None
 }
