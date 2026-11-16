
These secrets are stored and later accessed by the code as files:
--secret saas_user_management_system_authprov_google \
--secret saas_user_management_system_authprov_facebook \
--secret saas_user_management_system_authprov_saassocial_google \

I need to invent a method of accessing them via vault instead.
These are all passed into auth providers as clientSecretJSONFile


Examples:
{"clientSecretJSONFile": "/run/secrets/saas_user_management_system_authprov_google"}
{"clientSecretJSONFile": "/run/secrets/saas_user_management_system_authprov_facebook"}
{"clientSecretJSONFile": "/run/secrets/saas_user_management_system_authprov_google"}

I can not see saas_user_management_system_authprov_saassocial_google used anywhere

Step 1 -> Make google work with either
clientSecretJSONFile or clientSecretJSONVault
Step 2 -> Migrate all to vault
Step 4 -> Remove google secrets


Then repeat for faceboob

clientSecretJSONFile

Tenants:
usersystem: {"clientSecretJSONFile": "/run/secrets/saas_user_management_system_authprov_facebook"}
thumbsum: {"clientSecretJSONFile": "/run/secrets/saas_user_management_system_authprov_facebook"}
linkvis: {"clientSecretJSONFile": "/run/secrets/saas_user_management_system_authprov_facebook"}
thumbsumstage: {"clientSecretJSONFile": "/run/secrets/saas_user_management_system_authprov_facebook"}
challengeapp: {"clientSecretJSONFile": "/run/secrets/saas_user_management_system_authprov_facebook"}



# Gateway config
The gateway config class puts extra claims in the JWT token to be read by a gateway
In this case it just adds "kong_iss"
It is not about the gateway user management uses - rather about the service.
I need to keep this in and it doesn't need changing
