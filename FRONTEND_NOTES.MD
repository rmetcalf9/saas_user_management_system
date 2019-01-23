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

## Example Public Web Access

External Through Kong: https://somefunnyhostname.com/vx/public/web/***
***

## Example Public API Access

External Through Kong: https://somefunnyhostname.com/vx/public/api/login/serverinfo
Direct on Server: http://somefunnyhostname.com:5098/api/public/login/serverinfo

## Example Authed API Access

External Through Kong: https://somefunnyhostname.com/vx/authed/api/admin/tenantname/tenants
Direct on Server: http://somefunnyhostname.com:5098/api/authed/admin/tenantname/tenants


## For webapps calling service

API Prefix possibilities are:
/vx/
http://somefunnyhostname.com:8098/
http://somefunnyhostname.com:5098/
http://127.0.0.1:8098/

To call an API two paramas are needed, authed and api
authed is true or false
api is "/admin/tenantname/tenants" or "/login/serverinfo"

If Authed this maps to:
apiPrefix + '/authed/api' + api
Not Authed:
apiPrefix + '/public/api' + api





