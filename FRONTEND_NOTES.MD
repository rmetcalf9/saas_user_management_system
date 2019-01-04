# Notes for the frontend

The frontend is the userinterface for the management system

Endpoints setup in Kong
/vx/__tenant__/public
/vx/__tenant__/adminapi

## Login Web Endpoints (public)

### /vx/__tenant__/public/web/login

If there is only one auth provider configured will go direct to that authprovider, otherwise it will display a menu.

### /vx/__tenant__/public/web/login/__authprovidername__

Depending on authprovider configuration will display a page prompting the user for credentials.


## Login Service Endpoints (public)

### GET /vx/__tenant__/public/loginapi/authproviders

Get a list of the auth providers for this tenant

### GET /vx/__tenant__/public/loginapi/authproviders/__authprovidername__

Get info for a particular authprovider

### POST /vx/__tenant__/public/loginapi/authproviders/__authprovidername__

Login to a particular auth provider - will return the JWT token or an error

## Admin Web Endpoints (public)

### /vx/__tenant__/public/web/admin

## Admin Service Endpoints (protected using valid api token)

### /vx/__tenant__/adminapi

