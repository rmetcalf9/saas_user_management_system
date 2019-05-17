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



