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
