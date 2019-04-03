#!/bin/bash

echo "Preforms steps required for a codefresh release"

export START_DIR=$(pwd)
export GITROOT=${START_DIR}
export CMD_DOCKER=docker
export CMD_GIT=git



DOCKER_USERNAME=metcarob
DOCKER_IMAGENAME=saas_user_managmenet_system
cd ${GITROOT}

echo "Ensuring there are no local changes"
#if [[ `${CMD_GIT} status --porcelain` ]]; then
#  echo ""
#  echo "Error - there are local changes commit these before continuing"
#  exit 1
#fi

VERSIONFILE=${GITROOT}/VERSION
echo "Version file is ${VERSIONFILE}"
cd ${START_DIR}
./bumpVersion.sh ${VERSIONFILE}
RES=$?
if [ ${RES} -ne 0 ]; then
  cd ${START_DIR}
  echo ""
  echo "Bump version failed"
  exit 1
fi
VERSIONNUM=$(cat ${VERSIONFILE})

cd ${GITROOT}
${CMD_GIT} add -A
${CMD_GIT} commit -m "version ${VERSIONNUM}"
${CMD_GIT} tag -a "${VERSIONNUM}" -m "version ${VERSIONNUM}"
${CMD_GIT} push
RES=$?
if [ ${RES} -ne 0 ]; then
  cd ${START_DIR}
  echo ""
  echo "Failed to push to git. You need to run the following commands manually to complete:"f
  echo " git push"
  echo " git push --tags"
  echo " ${CMD_DOCKER} tag ${DOCKER_USERNAME}/${DOCKER_IMAGENAME}:latest ${DOCKER_USERNAME}/${DOCKER_IMAGENAME}:${VERSIONNUM}"
  exit 1
fi

${CMD_GIT} push --tags

echo "Script Complete"

cd ${START_DIR}
exit 0