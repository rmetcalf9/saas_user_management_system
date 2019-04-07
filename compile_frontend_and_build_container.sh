#!/bin/bash

#Not used by codefresh as I am using build container instead

#working directory is always saas_user_management_system root
GITROOT=$(pwd)
DOCKER_USERNAME=metcarob
DOCKER_IMAGENAME=saas_user_managmenet_system
VERSIONNUM=$(cat ./VERSION)

function build_quasar_app {
  APPNAME=${1}
  echo "Executing Quasar webfrontend build"
  cd ${GITROOT}/${APPNAME}
  if [ -d ./dist ]; then
    rm -rf dist
  fi
  if [ -d ./dist ]; then
    echo "ERROR - failed to delete dist directory"
    cd ${GITROOT}
    exit 1
  fi
  eval quasar build
  RES=$?
  if [ ${RES} -ne 0 ]; then
    cd ${GITROOT}
    echo ""
    echo "Quasar build failed for ${APPNAME}"
    exit 1
  fi
  if [ ! -d ./dist ]; then
    echo "ERROR - build command didn't create ${APPNAME}/dist directory"
    cd ${GITROOT}
    exit 1
  fi
}  

docker image inspect ${DOCKER_USERNAME}/${DOCKER_IMAGENAME}:${VERSIONNUM}_localbuild > /dev/null
RES=$?
if [ ${RES} -eq 0 ]; then
  docker rmi ${DOCKER_USERNAME}/${DOCKER_IMAGENAME}:${VERSIONNUM}_localbuild
  RES2=$?
  if [ ${RES2} -ne 0 ]; then
    echo "Image exists and delete failed"
    exit 1
  fi
fi



build_quasar_app frontend
RES=$?
if [ ${RES} -ne 0 ]; then
  exit 1
fi
build_quasar_app adminfrontend
RES=$?
if [ ${RES} -ne 0 ]; then
  exit 1
fi

echo "Build docker container (VERSIONNUM=${VERSIONNUM})"
#This file does no version bumping
cd ${GITROOT}
eval docker build . -t ${DOCKER_USERNAME}/${DOCKER_IMAGENAME}:${VERSIONNUM}_localbuild
RES=$?
if [ ${RES} -ne 0 ]; then
  echo ""
  echo "Docker build failed"
  exit 1
fi

exit 0
