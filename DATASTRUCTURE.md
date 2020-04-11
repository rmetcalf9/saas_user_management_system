# Internal data structures

User >-< Person --< UserAuth


Tenants
 - Name (Unique key)
 - Description
 - AllowUserCreation (if true signing up for the first time with a new id allows creation - if auth provider allows)
 - AuthProviders
   - GUID
   - MenuText
   - IconLink
   - Type (Internal, Google, etc)
   - AllowUserCreation (user creation only allowed if both tennat and authprovider have true)
   - ConfigJSON

Roles
 - Name (Unique key)

Users
 - UserID (Unique key)
 - TenantRoles (List of tenant name and roles exactly how it appears in the JWT token)

Implements a many to many relationship between Users and Auths, so one auth can be used for many users.
Identities
 - guid (Unique key)
 - UserID (UserID and IdentityID TOGETHER are the primary key)
 - Name
 - Description

Person
 - guid

UserAuths
 - AuthUserKey (Unique Key - includes provider type based on makeKey)
 - AuthProviderType
 - AuthProviderJSON
 - PersonGUID
 
APIKeys
 -  See [apikeys doc](./APIKEYS.md) for structure