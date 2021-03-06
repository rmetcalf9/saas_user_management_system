#!/bin/bash

PYTHON_CMD=python3
if [ E${EXTPYTHONCMD} != "E" ]; then
  PYTHON_CMD=${EXTPYTHONCMD}
fi

PYTHONVERSIONCHECKSCRIPT="import sys\nprint(\"Python version \" + str(sys.version_info))\nif sys.version_info[0] < 3:\n  exit(1)\nif sys.version_info[0] == 3:\n  if sys.version_info[1] < 6:\n    exit(1)\nexit(0)\n"
printf "${PYTHONVERSIONCHECKSCRIPT}" | ${PYTHON_CMD}
RES=$?
if [ ${RES} -ne 0 ]; then
  echo "Wrong python version - this version won't have all the required libraries"
  echo "Using command ${PYTHON_CMD}"
  echo "you can set enviroment variable EXTPYTHONCMD to make this script use a different python command"
  echo ""
  exit 1
fi

if [ E${EXTURL} = "E" ]; then
  echo "EXTURL not set"
  exit 1
fi
if [ E${EXTPORT} = "E" ]; then
  echo "EXTPORT not set"
  exit 1
fi

APP_DIR=.

export APIAPP_MODE=DEVELOPER
export APIAPP_JWTSECRET="gldskajld435sFFkfjlkfdsj"
export APIAPP_FRONTEND=_
export APIAPP_APIURL=${EXTURL}:${EXTPORT}/api
export APIAPP_APIDOCSURL=${EXTURL}:${EXTPORT}/apidocs
export APIAPP_FRONTENDURL=http://localhost:8081  #${EXTURL}:${EXTPORT}/frontend
export APIAPP_APIACCESSSECURITY=[]
export APIAPP_PORT=8098
export APIAPP_MASTERPASSWORDFORPASSHASH=ABC
export APIAPP_DEFAULTHOMEADMINUSERNAME=admin
export APIAPP_DEFAULTHOMEADMINPASSWORD=admin
##export APIAPP_JWT_TOKEN_TIMEOUT=3   #2 seconds, default is 5 minutes Use default
##export APIAPP_REFRESH_TOKEN_TIMEOUT=5  #30 seconds, default is 2 hours
export APIAPP_OBJECTSTORECONFIG="{\"Type\":\"Memory\"}"
##export APIAPP_OBJECTSTORECONFIG="{\"Type\":\"SQLAlchemy\", \"connectionString\":\"mysql+pymysql://saas_user_man_user:saas_user_man_testing_password@127.0.0.1:10103/saas_user_man_rad\"}"
##export APIAPP_GATEWAYINTERFACECONFIG "{\"Type\": \"none\", \"jwtSecret\":\"some_secretxx\", "kongISS": "kong_iss"}"
export APIAPP_DEFAULTMASTERTENANTJWTCOLLECTIONALLOWEDORIGINFIELD="http://localhost, http://somefunnyhostname.com:5081, http://somefunnyhostname.com:5082, http://localhost:8081, http://localhost:8082"
#export APIAPP_AUTOCONFIG="{ \"steps\": [{ \"type\": \"echo\", \"data\": { \"text\": \"Hello World\"}}]}"
#export APIAPP_AUTOCONFIGFILE=/home/IC.AC.UK/rjmetcal/sideGIT/saas_linkvis/services/_start_local_saas_user_management_service_config.json


export APIAPP_VERSION=
if [ -f ${APP_DIR}/VERSION ]; then
  APIAPP_VERSION=${0}-$(cat ${APP_DIR}/VERSION)
fi
if [ -f ${APP_DIR}/../VERSION ]; then
  APIAPP_VERSION=${0}-$(cat ${APP_DIR}/../VERSION)
fi
if [ -f ${APP_DIR}/../../VERSION ]; then
  APIAPP_VERSION=${0}-$(cat ${APP_DIR}/../../VERSION)
fi
if [ E${APIAPP_VERSION} = 'E' ]; then
  echo 'Can not find version file in standard locations'
  exit 1
fi


#Python app reads parameters from environment variables
${PYTHON_CMD} ./src/app.py
