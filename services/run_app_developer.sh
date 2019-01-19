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
export APIAPP_FRONTEND=_
export APIAPP_APIURL=${EXTURL}:${EXTPORT}/api
export APIAPP_APIDOCSURL=${EXTURL}:${EXTPORT}/apidocs
export APIAPP_FRONTENDURL=${EXTURL}:${EXTPORT}/frontend
export APIAPP_APIACCESSSECURITY=[]
export APIAPP_PORT=8098
export APIAPP_MASTERPASSWORDFORPASSHASH=ABC
export APIAPP_DEFAULTHOMEADMINUSERNAME=admin
export APIAPP_DEFAULTHOMEADMINPASSWORD=admin


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
