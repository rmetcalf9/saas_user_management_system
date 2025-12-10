#!/usr/bin/env bash
set -euo pipefail

echo "Script creates or recreates approles"
echo " if recrate will reset password but NOT change the policy"

CURDIR=$(pwd)
cd ../../
source ./_repo_vars.sh

POLICY_NAME=approle_deployment_${PROJECT_NAME}
APPROLE_NAME=deploy_${PROJECT_NAME}

echo "Running for ${PROJECT_NAME}"
echo " approle vault secret location ${VAULT_DEPLOYMENT_APPROLE_SECRET_LOCATION}"

if vault list -format=json auth/approle/role | jq -e ".[] | select(.==\"${APPROLE_NAME}\")" >/dev/null; then
    echo "AppRole '${APPROLE_NAME}' already exists. Delete and recreate (leave policy alone)."
    vault delete auth/approle/role/"${APPROLE_NAME}"
fi

# Check if the Vault policy exists
if vault policy list | grep -qw "${POLICY_NAME}"; then
    echo "Policy '${POLICY_NAME}' already exists. this script will not change it"
else
  echo "Creating policy ${POLICY_NAME} for approle: ${VAULT_DEPLOYMENT_APPROLE_SECRET_LOCATION}"
  vault policy write "${POLICY_NAME}" - <<EOF
# AppRole policy for ${VAULT_DEPLOYMENT_APPROLE_SECRET_LOCATION}
# Example placeholder policy:
# path "kv/data/memset/socialchat/uploadbucket/dev" {
#   capabilities = ["read"]
# }
EOF
fi

echo "Creating AppRole: ${APPROLE_NAME}"
vault write auth/approle/role/"${APPROLE_NAME}" \
  token_policies="${POLICY_NAME}" \
  token_ttl="1h" \
  token_max_ttl="24h" >/dev/null
echo "AppRole created."

ROLE_ID=$(vault read -field=role_id auth/approle/role/"${APPROLE_NAME}"/role-id)
echo "Role ID captured: ${ROLE_ID}"

SECRET_ID=$(vault write -field=secret_id -f auth/approle/role/"${APPROLE_NAME}"/secret-id)
echo "Secret ID captured: ${SECRET_ID}"

echo "Storing credentials in Vault at ${VAULT_DEPLOYMENT_APPROLE_SECRET_LOCATION}"
vault kv put "kv/${VAULT_DEPLOYMENT_APPROLE_SECRET_LOCATION}" role_id="${ROLE_ID}" secret_id="${SECRET_ID}"
echo "Credentials stored successfully."


echo "Complete - new approle setup with new password."
cd ${CURDIR}
