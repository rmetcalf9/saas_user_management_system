#!/bin/bash

if [[ "E${SAASCODEFRESHTESTUSERPASSWORD}" == "E" ]]; then
  echo "You need to set SAASCODEFRESHTESTUSERPASSWORD to use this"
  exit 1
fi

docker run --rm --network main_net \
-e BASEURL_TO_TEST=https://api.metcarob.com/saas_user_management/test/v0 \
-e APIAPP_DEFAULTHOMEADMINUSERNAME=codefresh_test_user \
-e APIAPP_DEFAULTHOMEADMINPASSWORD=${SAASCODEFRESHTESTUSERPASSWORD} \
-e EXPECTED_CONTAINER_VERSION=$(cat ../../VERSION) \
-e RUNNINGVIAKONG="TRUE" \
--mount type=bind,source=$(pwd),target=/ext_volume metcarob/saas_user_management_systemtest:latest nosetests --rednose /ext_volume
