  docker service create --name "${RJM_DOCKER_SERVICE_NAME}" \
    --network main_net \
    --secret saas_user_management_system_objectstore_config_dynamodb \
    --secret saas_user_management_system_objectstore_hashpw \
    --secret saas_user_management_system_objectstore_adminpw \
    --secret saas_user_management_system_gateway_config \
    --secret saas_jwtsecret \
    --secret saas_user_management_system_authprov_google \
    --secret saas_user_management_system_authprov_facebook \
    --secret saas_user_management_system_authprov_saassocial_google \
    -e APIAPP_PROJECT_NAME=${PROJECT_NAME} \
    -e APIAPP_JWTSECRETFILE=/run/secrets/saas_jwtsecret \
    -e APIAPP_GATEWAYINTERFACECONFIGFILE=/run/secrets/saas_user_management_system_gateway_config \
    -e APIAPP_OBJECTSTORECONFIGFILE=/run/secrets/saas_user_management_system_objectstore_config_dynamodb \
    -e APIAPP_MASTERPASSWORDFORPASSHASHFILE=/run/secrets/saas_user_management_system_objectstore_hashpw \
    -e APIAPP_DEFAULTHOMEADMINPASSWORDFILE=/run/secrets/saas_user_management_system_objectstore_adminpw \
    -e APIAPP_DEFAULTHOMEADMINUSERNAME=admin \
    -e APIAPP_APIURL=https://api.metcarob.com/api \
    -e APIAPP_APIDOCSURL=https://api.metcarob.com/saas_user_management/v${RJM_MAJOR_VERSION}/public/web/apidocs \
    -e APIAPP_FRONTENDURL=https://api.metcarob.com/saas_user_management/v${RJM_MAJOR_VERSION}/public/web/frontend \
    -e APIAPP_DEFAULTMASTERTENANTJWTCOLLECTIONALLOWEDORIGINFIELD="https://api.metcarob.com,https://localhost,http://localhost" \
    -e APIAPP_OBJECTSTOREDETAILLOGGING="N" \
    --constraint 'node.labels.legacy == true' \
    "metcarob/saas_user_management:${RJM_VERSION}"
  
# Secrets that are used by app

Goal 1 Migrate APIAPP_JWTSECRETFILE so it is in vault instead
we can do this with:
"APIAPP_JWTSECRETVAULT": "/asfplatform/webapps/_common:APIAPP_JWTSECRET"
if we have a valid vault role and secret

I think the role will be approle_run_dev_webapp_

On new server there will be secrets:
webapp_saas_user_management_vault_role_id
webapp_saas_user_management_vault_secret_id

These are read into the template as
        "--secret", f"webapp_{project_name}_vault_role_id",
        "--secret", f"webapp_{project_name}_vault_secret_id",
        "-e", "APIAPP_VAULT_URL=https://vault.metcarob.com/",
        "-e", f"APIAPP_VAULT_ROLE_IDFILE=/run/secrets/webapp_{project_name}_vault_role_id",
        "-e", f"APIAPP_VAULT_SECRET_IDFILE=/run/secrets/webapp_{project_name}_vault_secret_id"

I think I can add this to my memset deploy for this

