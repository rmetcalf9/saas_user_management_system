#!/bin/bash

#Not used by codefresh as I am using build container instead
source ./_repo_vars.sh


#working directory is always saas_user_management_system root
GITROOT=$(pwd)
DOCKER_IMAGENAME=${PROJECT_NAME}
VERSIONNUM=${RJM_VERSION}

echo "compile_fronent_and_build_container.sh - inspecting image"
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

echo "Skipping frontend as it can not build locally"
# docker run --rm --name docker_build_quasar_app --mount type=bind,source=${GITROOT}/${APPNAME}/frontend,target=/ext_volume ${QUASARBUILDIMAGE} -c "build_quasar_app /ext_volume spa \"local_build_${VERSIONNUM}\""
# RES=$?
# if [ ${RES} -ne 0 ]; then
#   exit 1
# fi

# old space was 2048
# now trying 1536
docker run --rm --name docker_build_quasar_app \
  --mount type=bind,source=${GITROOT}/${APPNAME}/adminfrontend,target=/ext_volume \
  -e OVERRIDE_PUBLIC_PATH= \
  ${QUASARBUILDIMAGE_ADMINFRONTEND} \
  -c "build_quasar_app /ext_volume pwa \"local_build_${VERSIONNUM}\"" 1536
RES=$?
if [ ${RES} -ne 0 ]; then
  exit 1
fi

if [ ! -d ${GITROOT}/${APPNAME}/frontend/dist/spa ]; then
  echo "ERROR - build command didn't create ${GITROOT}/${APPNAME}/frontend/dist/spa directory"
  cd ${GITROOT}
  exit 1
fi
if [ ! -d ${GITROOT}/${APPNAME}/adminfrontend/dist/pwa ]; then
  echo "ERROR - build command didn't create ${GITROOT}/${APPNAME}/adminfrontend/dist/spa directory"
  cd ${GITROOT}
  exit 1
fi

echo "Stopping after quasar builds"
exit 0

echo "Build docker container (VERSIONNUM=${VERSIONNUM})"
echo "docker build . -t ${DOCKER_USERNAME}/${DOCKER_IMAGENAME}:${VERSIONNUM}_localbuild"
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
