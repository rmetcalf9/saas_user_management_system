#!/bin/bash

#Not used by codefresh as I am using build container instead

#working directory is always saas_user_management_system root
GITROOT=$(pwd)
DOCKER_USERNAME=metcarob
DOCKER_IMAGENAME=saas_user_managmenet_system
VERSIONNUM=$(cat ./VERSION)

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

docker run --rm --name docker_build_quasar_app --mount type=bind,source=${GITROOT}/${APPNAME}/frontend,target=/ext_volume metcarob/docker-build-quasar-app:0.0.6 -c "build_quasar_app /ext_volume spa"
RES=$?
if [ ${RES} -ne 0 ]; then
  exit 1
fi
docker run --rm --name docker_build_quasar_app --mount type=bind,source=${GITROOT}/${APPNAME}/adminfrontend,target=/ext_volume metcarob/docker-build-quasar-app:0.0.6 -c "build_quasar_app /ext_volume spa"
RES=$?
if [ ${RES} -ne 0 ]; then
  exit 1
fi

if [ ! -d ${GITROOT}/${APPNAME}/frontend/dist/spa ]; then
  echo "ERROR - build command didn't create ${GITROOT}/${APPNAME}/frontend/dist/spa directory"
  cd ${GITROOT}
  exit 1
fi
if [ ! -d ${GITROOT}/${APPNAME}/adminfrontend/dist/spa ]; then
  echo "ERROR - build command didn't create ${GITROOT}/${APPNAME}/adminfrontend/dist/spa directory"
  cd ${GITROOT}
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
