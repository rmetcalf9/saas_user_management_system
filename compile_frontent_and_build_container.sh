#!/bin/bash

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
eval docker build . -t ${DOCKER_USERNAME}/${DOCKER_IMAGENAME}:latest
RES=$?
if [ ${RES} -ne 0 ]; then
  echo ""
  echo "Docker build failed"
  exit 1
fi
docker tag ${DOCKER_USERNAME}/${DOCKER_IMAGENAME}:latest ${DOCKER_USERNAME}/${DOCKER_IMAGENAME}:${VERSIONNUM}
RES=$?
if [ ${RES} -ne 0 ]; then
  echo ""
  echo "Docker tag failed"
  exit 1
fi

exit 0
