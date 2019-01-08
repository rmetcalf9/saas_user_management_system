# Notes for the frontend

The frontend is the userinterface for the management system

Endpoints setup in Kong
 - /vx/public
 - /vx/adminapi

Nginx paths: (In docker container nginx servers on single port)
 - /vx/public/__web__
 - /vx/public/__api__
 - /vx/adminapi/__adminapi__

On development machine these must run on different ports:
 - /vx/public/__web__  -> / (8091)
 - /vx/public/__api__  -> / (8098)
 - /vx/adminapi/__adminapi__  -> / (8099)
 
Frontend globalDataSTore action checkAuthProviders has logic to navigate this
 
## Login Web Endpoints (public)

### /vx/public/web/$$tenant$$/login

If there is only one auth provider configured will go direct to that authprovider, otherwise it will display a menu.

### /vx/public/web/$$tenant$$/login/__authprovidername__

Depending on authprovider configuration will display a page prompting the user for credentials.


## Login Service Endpoints (public)

### GET /vx/public/api/login/$$tenant$$/authproviders

Get a list of the auth providers for this tenant

### POST /vx/public/api/login/$$tenant$$/authproviders/auth

Login to a particular auth provider - will return the JWT token or an error

## Admin Web Endpoints (public)

### /vx/public/web/$$tenant$$/admin

## Admin Service Endpoints (protected using valid api token)

### /vx/adminapi/$$tenant$$??????

