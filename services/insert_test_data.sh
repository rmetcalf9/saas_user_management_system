#!/bin/bash

echo "Insert Test Data"
if [[ $# -eq 1 ]]; then
  echo "Sleeping for ${1} seconds to allow services to start"
  sleep ${1}
fi

export APIAPP_MODE=DEVELOPER
export APIAPP_FRONTEND=_
export APIAPP_APIURL=${EXTURL}:${EXTPORT}/api
export APIAPP_APIDOCSURL=${EXTURL}:${EXTPORT}/apidocs
export APIAPP_FRONTENDURL=${EXTURL}:${EXTPORT}/frontend
export APIAPP_APIACCESSSECURITY=[]
export APIAPP_PORT=8098
export APIAPP_MASTERPASSWORDFORPASSHASH=ABC
export APIAPP_DEFAULTHOMEADMINUSERNAME=admin
export APIAPP_DEFAULTHOMEADMINPASSWORD=admin

python3 ./src/insert_test_data.py

exit 0