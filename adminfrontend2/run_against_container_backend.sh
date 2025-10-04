#!/bin/bash

echo "Run adminfrontend and a user management container"
echo "user to test adminfrontend only - but uses contianers backend"
echo " relies on current script start_local_saas_user_management_service"

INITAL_DIR=$(pwd)

cd ..
source ./_repo_vars.sh
cd ${INITAL_DIR}

echo " using container version ${RJM_USERMANAGEMENT_CONTAINER}"

export APIAPP_JWTSECRET="gldskajld435sFFkfjlkfdsj"
export SAAS_APIAPP_MASTERPASSWORDFORPASSHASH=wefgFvGFt5433e

# 8099 is hard coded in the saas_user_management container (Shared functions)
#  compiled into the webapp in the part where it identifies backend api
#  in this project in saasLinkvisCallapi.js
EXTPORT80FORSECURITY=8099


if [ E${EXTURL} = "E" ]; then
  echo "EXTURL not set"
  exit 1
fi
if [ E${EXTPORT} = "E" ]; then
  echo "EXTPORT not set"
  exit 1
fi


#./_start_local_saas_user_management_service.sh ${SAAS_USERMANAGEMENT_CONTAINER} \
#  ${APIAPP_JWTSECRET} \
#  ${EXTURL} \
#  ${EXTPORT} \
#  ${EXTPORT80FORSECURITY} \
#  ${SAAS_APIAPP_MASTERPASSWORDFORPASSHASH}

APIAPP_COMMON_ACCESSCONTROLALLOWORIGIN="http://127.0.0.1:8082,http://localhost:8082"
SETUP_JSON_DIR=${INITAL_DIR}
SETUP_JSON_FILENAME="_start_local_saas_user_management_service_config.json"
EXPECTED_TENANT="usersystem"


start_local_saas_user_management_service \
 ${RJM_USERMANAGEMENT_CONTAINER} \
 ${APIAPP_JWTSECRET} \
 ${EXTURL} \
 ${EXTPORT} \
 ${EXTPORT80FORSECURITY} \
 ${SAAS_APIAPP_MASTERPASSWORDFORPASSHASH} \
 ${APIAPP_COMMON_ACCESSCONTROLALLOWORIGIN} \
 ${SETUP_JSON_DIR} \
 ${SETUP_JSON_FILENAME} \
 ${EXPECTED_TENANT}

RES=$?
if [ ${RES} -ne 0 ]; then
 echo "Error starting security microservice"
 echo ""
 exit 1
fi

echo "Security microservice started"
echo ""

echo "run_against_container_backend.sh"
