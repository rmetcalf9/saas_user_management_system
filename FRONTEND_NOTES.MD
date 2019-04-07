# Notes for the frontend

The frontend is the userinterface for the management system

## Endpoint Setup

 | Type of Access      | run_all_parts_on_dev_machine       | Container on dev machine (expose port 80)   | container via Kong redirects | Nice Test URL                                    |
 |---|---|---|---|---|
 | login Webpage       | http://host:8081/                  | http://host:80/public/web/frontend/#/       | https://api.metcarob.com/saas_user_management/test/v0/public/web/frontend/      | http://host:X/frontend/#/                 |
 | login Admin Webpage | http://host:8082/                  | http://host:80/public/web/adminfrontend/#/  | https://api.metcarob.com/saas_user_management/test/v0/public/web/adminfrontend/ | http://host:X/adminfrontend/#/usersystem  |
 | public login API    | http://host:8098/api/public/login/ | http://host:80/api/public/login/            |                              | http://host:X/api/public/login/serverinfo |
 | authed admin API    | http://host:8098/api/authed/admin/ | http://host:80/api/authed/admin/            |                              |                                           |
 | API Docs            | http://host:8098/apidocs/          | http://host:80/public/web/apidocs/          | https://api.metcarob.com/saas_user_management/test/v0/public/web/apidocs/       |                                           |

Note: due to Python limitations the API switchs from /api/public to /public/api because python needs it one way and Kong security needs it the other way round. This is only for the api section and dosen't affect the web.

Remove /test/ for prod endpoint 
 
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





