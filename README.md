# saas_user_management_system
Generic SAAS user account management Microservice which preforms authorization and authentication and gives clients JWT tokens to gain access to other services.

## Features

 - *Multi Tenant
 - *Support mutiple auth providers (Internal DB, google auth, facebook auth, SQRL, etc.)
 - *Login page (choose login method)
 - *New user signup process
 - *email verification
 - *Admin configuration web interface
 - *Manage roles
 - *Integrates with kong to setup consumers and allow kong to secure services
 
 *Feature planned and not yet developed

## Notes for Client Web Apps

Generally client web apps are setup to work from the same URL as the login endpoint enabling cookies to be shared.

### User login

 - Direct browser to /login/tennant_name endpoint passing a return URL as browser paramater
 - Once auth is completed a cookie named jwt-auth-cookie is set in the users browser and the user is sent to the return URL
 - Client Web Apps can use the jwt token to determine the username, tennants the user has access to and roles the user has configured
 - Client Web Apps can send the jwt token as auth header when calling services 
 
### Token renewal

JWT tokens will expire and need to be renewed.

PROCESS TODO


## Notes for Service

Services should be set up to validate the JWT token. (This can be easily achieved by using the Kong jwt plugin.)

TODO


## Technical Information

### JWT Token Structure

Example token:
```
{
  "iss": "saas_user_management_system_jwtkey",
  "exp": 1546520660,
  "userid": "xxx@yyy.com",
  "tennant_info": [
    {
     "name": "tennant1",
     "roles": [
      "role1", "role2", "role3"
     ]
    },
    {
     "name": "tennant2",
     "roles": [
      "role1", "role2", "role3"
     ]
    }
  ]
}
```

userid is the unique identifier for each user. Since a single user can have mutiple auth providers setup it may be different depending on the auth provider used.

TODO - decide if this should be extended to contain more user information of if this should be implemented in a seperate microservice.


### Internal data structures

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
   - ConfigXML

Roles
 - Name (Unique key)

Users
 - UserID (Unique key)
 - Roles (List of role names)

UserAuths
 - UserID
 - Tenant
 - AuthProviderGUID
 - AuthXML (Data depends on auth provider type)

### Bootstrap

The user management system admin API uses the login endpoints for auth. To enable this to work the following process is run on startup if no data exists in the tenant datastore.

A tennant called "usersystem" is created with a single auth provider "internal", allowuser creation is false at both levels.
A user is setup in this tenant with the roles "loggedin" and "systemadmin". 
A userauth is setup for this userID against the "usersystem" tenant with username=APIAPP_DEFAULTHOMEADMINUSERNAME password=APIAPP_DEFAULTHOMEADMINPASSWORD.

The User Management master admin API's will only work with users of the "usersystem" tenant with the role "systemadmin" granted.

### Auto user creation

If an authprovider has allowusercreation enabled and it is also enabled against the tenant then users are created with the role "loggedin" when they first log in.

### Deployment

All components are designed to be deployed in a single container and a codefresh.yml file handles configuring Kong frontend.



