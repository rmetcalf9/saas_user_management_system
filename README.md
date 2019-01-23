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
	'UserID': 'abc123',
	'TenantRoles': {
		'tennantName': ['roleName']
	},
	'authedPersonGuid': '123ABC',
	'iss': 'abc123',
	'exp': 1548076970
}
```

userid is the unique identifier for each user. Since a single user can have mutiple auth providers setup it may be different depending on the auth provider used.

TODO - decide if this should be extended to contain more user information of if this should be implemented in a seperate microservice.

### Bootstrap

The user management system admin API uses the login endpoints for auth. To enable this to work the following process is run on startup if there is no tenant called "usersystem" in the tenant datastore.

A tennant called "usersystem" is created with a single auth provider "internal", allowuser creation is false at both levels.
A user is setup in this tenant with the roles "hasaccount" and "systemadmin".
An identity is setup for this user with Name=Description="standard"
A Person is setup and assigned this identity
A userauth is setup for against the "usersystem" tenant with username=APIAPP_DEFAULTHOMEADMINUSERNAME password=APIAPP_DEFAULTHOMEADMINPASSWORD.


The User Management master admin API's will only work with users of the "usersystem" tenant with the role "systemadmin" granted.

### Auto user creation

If an authprovider has allowusercreation enabled and it is also enabled against the tenant then users are created with the role "hasaccount" when they first log in.

### Deployment

All components are designed to be deployed in a single container and a codefresh.yml file handles configuring Kong frontend.


## Env Vars

APIAPP_MASTERPASSWORDFORPASSHASH - Must be set for security
APIAPP_DEFAULTHOMEADMINUSERNAME -
APIAPP_DEFAULTHOMEADMINPASSWORD  -
APIAPP_GATEWAYINTERFACETYPE
APIAPP_GATEWAYINTERFACECONFIG
APIAPP_JWT_TOKEN_TIMEOUT - Number of seconds the jwt tokens are valid for Defaulted to 5 minutes
APIAPP_REFRESH_TOKEN_TIMEOUT - Number of seconds the jwt tokens are valid for, must be greater than APIAPP_JWT_TOKEN_TIMEOUT. Defaulted to 10 minutes
APIAPP_REFRESH_SESSION_TIMEOUT- Number of seconds the refresh tokens are valid for. Once this timout has finished users are forced to resupply credentials. must be greater than APIAPP_REFRESH_TOKEN_TIMEOUT. Defaulted to 2 hours.

APIAPP_EBOAPIDOCSURL
