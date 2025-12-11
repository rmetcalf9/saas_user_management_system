#!/bin/bash

export PROJECT_NAME=${PWD##*/}          # to assign to a variable
export PROJECT_NAME=${PROJECT_NAME:-/}

export RJM_VERSION=$(cat ./VERSION)
export RJM_VERSION_UNDERSCORE=$(cat ./VERSION | tr '.' '_')
export RJM_MAJOR_VERSION=$(echo ${RJM_VERSION%%.*})
export RJM_DOCKER_SERVICE_NAME=${PROJECT_NAME}_${RJM_VERSION_UNDERSCORE}
export QUASARBUILDIMAGE="metcarob/docker-build-quasar-app:0.0.12"
export QUASARBUILDIMAGE_ADMINFRONTEND="metcarob/docker-build-quasar-app:0.0.33"
export RJM_DOCKERWSCALLER_IMAGE="metcarob/docker-ws-caller:0.7.19"
export RJM_DOCKER_KONG_API_URL="http://tasks.kong:8001"
export RJM_DOCKER_SERVICE_URL=tasks.${RJM_DOCKER_SERVICE_NAME}
export JWT_COOKIE_NAME="jwt-auth-token"
export AUTHED_ACL_WHITELIST="saas_user_management"
export AUTHED_ACL_BLACKLIST=""
export RJM_KONG_UPSTREAM_NAME=${PROJECT_NAME}_${RJM_MAJOR_VERSION}

export RJM_PYTHON_TEST_IMAGE=python:3.10

export DOCKER_USERNAME=metcarob

export RJM_USERMANAGEMENT_CONTAINER="metcarob/saas_user_management:0.0.224_rootver"

export VAULT_DEPLOYMENT_APPROLE_SECRET_LOCATION=/deploymentapproles/${PROJECT_NAME}

