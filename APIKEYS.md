# API Keys in User Management System

## Data Structure

APIKey
{
    id: guid of API key,
    tenantid: id of tenant,
    createdByUserID: userID who created the API key.
    restrictedToRoles: [] list of roles this API key is restricted to - undefined means all user roles are granted 
}

## Role inheritance
API Keys inherit the roles they are granted from the user that created them. When the inital login is processed the roles are added

### Restrict roles
If this property is set only roles appearing in this list are included in the API key.

### Should API Keys belong to mutiple users
If an integration relies on an API key it is possible the user will leave then the integration break. One possible solution would be for the same API key to be shared amounst mutiple users. This is a possible future enhancement but will not be included in V1.

### Login method roles
Any roles assigned only via the login method are not assigned to the API key.

### Expiring roles
Should I implement expiring roles first - See https://github.com/rmetcalf9/saas_user_management_system/issues/14
This issue describes changes to the roles held in the user not in the JWT token. The APIToken will have the same process for creating the JWT token as the user ID so these changes can be mirrored.

## Should APIKeys use refresh system
An APIKey login will generate a JWT token using the same method so it should use the refresh system.

## API Key control properties
I will use the same properties as it's actually JWT token properties.

## Service calls required

### Admin calls all for Tenant and UserID auther by userID 

Part of login api (public/login) under APIlogin_APIKeys.py

 - /<string:tenant>/apikeys GET - API Key List for tenant & userID combo
 - /<string:tenant>/apikeys POST - Add API Key tenant & user ID
 - /<string:tenant>/apikeys/<string:apikey> DELETE Delete API Key (no edit for different roles, just delete and reissue)

### Login
Existing login call -> Accept API Keys. No creation allowed in this method
