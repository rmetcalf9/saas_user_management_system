# How to use the user system as part of a Webapplication

Developers should read this page when planning to use the user system as the login process for your own webapp.

## Presumption

This page prusumes the user management system is accessed thorugh the same URL as where the client gets the application. (This can be behind a reverse proxy)

## Overview of the process

This is a simple swimlane diagram showing the process


## A simple login process

 | Client App running on web browser | SAAS User Management Frontend App | Protected Services |
 |----|---|---|
 | On page load client app checks if it has a cookie 'usersystemUserCredentials' and finds no cookie is set |
 | Client app fowards the user to /vx/public/web/$$tenant$$/login with param usersystem_returnaddress set to the return url used later|
 | | User logs in and if sucessful sets usersystemUserCredentials cookie with JWTToken and Refresh Token |
 | | App forwards the user to the returnaddress URL that was supplied |
 | On page load client app sees the cookie |
 | Client app makes calls to protected services with JWTToken |
 | | | Protected services validate the cookie, either locally or by APIGateway configuration |
 | | | Protected services can use data inside the JWTToken to confirm user info |
 
## The JWTToken will timeout after APIAPP_JWT_TOKEN_TIMEOUT seconds (default 60 * 5 = 5 minutes)

 | Client App running on web browser | SAAS User Management Frontend App | Protected Services |
 |----|---|---|
 | Client app makes calls to protected services with JWTToken |
 | | | JWT Expired an error is returned |
 | Client calls SAAS JSON endpoint GET /vx/public/api/refresh/$$tenant$$ |
 | | Refresh token is validated and a new JWTToken and Refresh Token is returned in service response. Refresh tokens expire after APIAPP_REFRESH_TOKEN_TIMEOUT but each new token extends this time again. The maximum extension without a new log in is set by APIAPP_REFRESH_SESSION_TIMEOUT |
 | Client updates it's cookie with new Refresh and JWTTokens |
 | Client continues to call services as normal |

In the case of an expired refresh token, or if the refresh session has expired the client will need to use the login process. (Causing the user to resupply credentials)



