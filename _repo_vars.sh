#!/bin/bash

export PROJECT_NAME=${PWD##*/}          # to assign to a variable
export PROJECT_NAME=${PROJECT_NAME:-/}

export RJM_VERSION=$(cat ./VERSION)
export RJM_VERSION_UNDERSCORE=$(cat ./VERSION | tr '.' '_')
export RJM_MAJOR_VERSION=$(echo ${RJM_VERSION%%.*})
export RJM_DOCKER_SERVICE_NAME=${PROJECT_NAME}_${RJM_VERSION_UNDERSCORE}
export QUASARBUILDIMAGE="metcarob/docker-build-quasar-app:0.0.12"
export QUASARBUILDIMAGE_ADMINFRONTEND="metcarob/docker-build-quasar-app:0.0.33"

export DOCKER_USERNAME=metcarob

export RJM_USERMANAGEMENT_CONTAINER="metcarob/saas_user_management:0.0.224_rootver"
