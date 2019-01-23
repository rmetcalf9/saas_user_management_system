# Notes for the frontend

The frontend is the userinterface for the management system

Endpoints setup in Kong
 | Endpoint in Kong | Endpoint mapped to on server | Notes |
 |---|---|---|
 | /vx/public | /public | |
 | /vx/authed | /authed | Verifies JWT Tokens |

Nginx paths: (In docker container nginx servers on single port)
 | Nginx External Path | Mapped to |
 |---|---|
 | /public/web/frontend | frontend dist folder |
 | /public/web/adminfrontend | adminfrontend dist folder |
 | /public/api | /api/public |
 | /authed/api | /api/authed |

On development machine these must run on different ports, accessed by root on all:
 - /vx/public/__web__/frontend  -> / (8091)
 - /vx/public/__web__/adminfrontend  -> / (8092)
 - /vx/public/__api__  -> / (8098)
 
Frontend globalDataSTore action checkAuthProviders has logic to navigate this

## Server Info Endpoint

External Through Kong: https://somefunnyhostname.com/vx/public/api/serverinfo/
Internal Through nginx: /public/api/serverinfo/
Dev External: http://somefunnyhostname.com:8098/public/api/serverinfo/


## Login Web Endpoints (public)

### /vx/public/web/$$tenant$$/login

If there is only one auth provider configured will go direct to that authprovider, otherwise it will display a menu.

### /vx/public/web/$$tenant$$/login/__authprovidername__

Depending on authprovider configuration will display a page prompting the user for credentials.


## Login Service Endpoints (public)

### GET /vx/public/api/login/$$tenant$$/authproviders

Get a list of the auth providers for this tenant

### POST /vx/public/api/login/$$tenant$$/authproviders

Login to a particular auth provider - will return the JWT token or an error

### POST /vx/public/api/login/$$tenant$$/refresh

Login to a particular auth provider - will return the JWT token or an error


## Admin Web Endpoints (public)

### /vx/public/web/$$tenant$$/admin

## Admin Service Endpoints (protected using valid api token)

### GET /vx/authed/api/admin/$$tenant$$/tenants

Get a list of tenants

