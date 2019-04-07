#!/bin/bash

echo "Script to run a local container which can be accessed via container access descrubed in FRONTEND_NOTES"

if [[ ! -f ./VERSION ]]; then
  echo "VERSION dosen't exist - are you in correct directory?"
  exit 1
fi
export RJM_VERSION=$(cat ./VERSION)
export RJM_VERSION_UNDERSCORE=$(echo ${RJM_VERSION} | tr '.' '_')
export RJM_IMAGE_TO_RUN=metcarob/saas_user_managmenet_system:${RJM_VERSION}_localbuild
export RJM_RUNNING_SERVICE_NAME=saas_user_management_system_${RJM_VERSION_UNDERSCORE}_localbuild

echo "Launching image ${RJM_IMAGE_TO_RUN}"

##Check if container image exists
docker image inspect ${RJM_IMAGE_TO_RUN} > /dev/null
RES=$?
if [ ${RES} -ne 0 ]; then
  echo "Image dosen't exist"
  echo "Have you run compile_frontend_and_build_container.sh to generate ${RJM_IMAGE_TO_RUN}?"
  echo ""
  exit 1
fi

##TODO Check if running and error
docker service inspect ${RJM_RUNNING_SERVICE_NAME} > /dev/null
RES=$?
if [ ${RES} -ne 1 ]; then
  echo "Container already runing"
  echo "use service rm ${RJM_RUNNING_SERVICE_NAME} to stop"
  echo ""
  exit 1
fi

docker service create --name ${RJM_RUNNING_SERVICE_NAME} \
--network main_net \
--secret saas_user_management_system_objectstore_config \
--secret saas_user_management_system_objectstore_hashpw \
--secret saas_user_management_system_objectstore_adminpw \
-e APIAPP_OBJECTSTORECONFIGFILE=/run/secrets/saas_user_management_system_objectstore_config \
-e APIAPP_MASTERPASSWORDFORPASSHASHFILE=/run/secrets/saas_user_management_system_objectstore_hashpw \
-e APIAPP_DEFAULTHOMEADMINPASSWORDFILE=/run/secrets/saas_user_management_system_objectstore_adminpw \
-e APIAPP_DEFAULTHOMEADMINUSERNAME=admin \
-e APIAPP_APIURL=${EXTURL}:${EXTPORT}/api \
-e APIAPP_APIDOCSURL=${EXTURL}:${EXTPORT}/apidocs \
-e APIAPP_FRONTENDURL=${EXTURL}:${EXTPORT}/public/web/frontend \
--publish 80:80 \
${RJM_IMAGE_TO_RUN}
RES=$?
if [ ${RES} -ne 0 ]; then
  echo "Failed to start service"
  echo ""
  exit 1
fi

echo "Complete"
echo "Start from http://127.0.0.1/public/web/adminfrontend/#/"
echo ""
echo "End docker service rm ${RJM_RUNNING_SERVICE_NAME} to stop"
echo ""
exit 0
