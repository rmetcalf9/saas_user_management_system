# Auth Providers Documentation


## Internal

The internal auth provider will validate a user against a password held in the local data store.
Mutiple tenants can share the same lookup or have different lookups.

Example config:
```
"ConfigJSON": {
  "userSufix": "@internalDataStore"
}
```



## Google

A single google user maps to an auth. Setup in the google console and download the client secrets json file. Add it as a docker secret to secure it.

Example config:
```
"ConfigJSON": {
  "clientSecretJSONFile": "/run/secrets/saas_user_management_system_authprov_google"
}
```

## Facebook

Facebook auth only works from https endpoints

Example config:
```
"ConfigJSON": {
  "clientSecretJSONFile": "/run/secrets/saas_user_management_system_authprov_facebook"
}
```
## LDAP

Authenticate via LDAP server

"Type": "ldap",


Example config:
```
"ConfigJSON": {
  "Timeout": 60,
  "Host": "unixldap.somehost.com",
  "Port": "123",
  "UserBaseDN": "ou=People,ou=everyone,dc=somehost,dc=com",
  "UserAttribute": "uid",
  "GroupBaseDN": "ou=Group,ou=everyone,dc=somehost,dc=com",
  "GroupAttribute": "cn",
  "GroupMemberField": "memberUid",
  "userSufix": "@OrgNameLDAP",
  "MandatoryGroupList": "group1,group2,group3",
  "AnyGroupList": "group1,group2,group3"
}
```

GroupWhiteList: Users must be a memeber of at least one of these groups to be authenticated

#TODO Group to role mapping


## Apple

Config exmaple:
```
{"service_id": "app.socialclubhub.login"}
```

Frontend implementation notes (DEL when implemented):
AppleID.auth.init({
    clientId: "...",
    scope: "name email",
    redirectURI: "...",
    usePopup: true
});


const response = await AppleID.auth.signIn();

const identityToken = response.authorization.id_token;

await api.post("/login/apple", {
    token: identityToken
});



My auth providers:
{
    "guid": "fb27c553-9848-440d-94cf-7d1d032ddbad",
    "Type": "apple",
    "AllowUserCreation": false,
    "AllowLink": true,
    "AllowUnlink": true,
    "LinkText": "Link to apple account",
    "MenuText": "Login with Apple",
    "IconLink": "",
    "ConfigJSON": "{\"service_id\": \"app.socialclubhub.login\"}",
    "StaticlyLoadedData": {
        "client_id": "app.socialclubhub.login"
    },
    "saltForPasswordHashing": "JDJiJDEyJFg5RVBqbEhnNk1hQWs2UER5SE0xSC4="
}
