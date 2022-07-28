#!/bin/bash

echo "Only works on locally running container because /public/api and /public/web are not present"

if [[ "E${SAASCODEFRESHTESTUSERPASSWORD}" == "E" ]]; then
  echo "You need to set SAASCODEFRESHTESTUSERPASSWORD to use this"
  exit 1
fi

export HOSTIP=`ip -4 addr show scope global dev wlp2s0 | grep inet | awk '{print \$2}' | cut -d / -f 1`

docker run --rm --network main_net \
-e BASEURL_TO_TEST=http://${HOSTIP}:8098 \
-e APIAPP_DEFAULTHOMEADMINUSERNAME=admin \
-e APIAPP_DEFAULTHOMEADMINPASSWORD=admin \
-e EXPECTED_CONTAINER_VERSION=$(cat ../../VERSION) \
-e RUNNINGVIAKONG="TRUE" \
--mount type=bind,source=$(pwd),target=/ext_volume metcarob/saas_user_management_systemtest:latest python3 -m pytest /ext_volume
