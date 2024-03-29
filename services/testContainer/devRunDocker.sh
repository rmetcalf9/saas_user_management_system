#!/bin/bash

#File run on developers machine to test the container

cp ../src/constants.py copy_of_main_constants_do_not_edit.py

docker run --rm --network main_net \
-e BASEURL_TO_TEST=http://saas_user_management_system_$(cat ../../VERSION | tr '.' '_')_localbuild \
-e HTTPORIGIN_TO_TEST=http://localhost \
-e APIAPP_DEFAULTHOMEADMINUSERNAME=admin \
-e APIAPP_DEFAULTHOMEADMINPASSWORD=admin \
-e EXPECTED_CONTAINER_VERSION=$(cat ../../VERSION) \
--mount type=bind,source=$(pwd),target=/ext_volume metcarob/saas_user_management_systemtest:latest python3 -m pytest /ext_volume
