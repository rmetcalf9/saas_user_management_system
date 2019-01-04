#!/bin/bash

#Hardcoded here
export APIAPP_MODE=DOCKER

if [ E${APP_DIR} = "E" ]; then
  echo 'APP_DIR not set'
  exit 1
fi

export APIAPP_VERSION=
if [ -f ${APP_DIR}/../VERSION ]; then
  APIAPP_VERSION=$(cat ${APP_DIR}/../VERSION)
fi
if [ -f ${APP_DIR}/../../VERSION ]; then
  APIAPP_VERSION=$(cat ${APP_DIR}/../../VERSION)
fi
if [ E${APIAPP_VERSION} = 'E' ]; then
  echo 'Can not find version file in standard locations'
  exit 1
fi

_term() { 
  echo "run_app_docker.sh - Caught SIGTERM signal!" 
  kill -TERM "$child_nginx" 2>/dev/null
  kill -TERM "$child_uwsgi" 2>/dev/null
}

trap _term SIGTERM

#Find all params that start with API_APP and end with FILE and create mirror vars
AA=$(env | awk -F "=" '{print $1}' | grep "APIAPP_.*FILE$")
for i in ${AA}; do
  NEWVARNAME=${i::-4}
  FILETOREAD=$(eval echo \$${i})
  echo "${i} set so ${FILETOREAD} to be read and contents saved in var ${NEWVARNAME}"
  if [ ! -f ${FILETOREAD} ]; then
    echo "ERROR ${FILETOREAD} dosen't exist - continuing without setting env variable"
  else
    eval export ${NEWVARNAME}=$(cat ${FILETOREAD})
  fi
  #Check lines
  #RES=$(eval echo \$${NEWVARNAME})
  #echo "RES=${RES}"
done


##TODO Evaluate params from incomming variables
#VARSTOUPDATE=$(env | grep "^APIAPP_")
#C=0
#for i in ${VARSTOUPDATE}; do
#  ((C++))
#  eval "${i}"
#done
#echo "  ${C} variables evaluated"

uwsgi --ini /uwsgi.ini &
child_uwsgi=$! 
nginx -g 'daemon off;' &
child_nginx=$! 

wait "$child_uwsgi"

##wait "$child_nginx"
##Not waiting for nginx. Otherwise when python app terminates but nginx doesn't
## the container dosen't stop
## instead we kill nginx if the python app has stopped
kill -TERM "$child_nginx" 2>/dev/null
wait "$child_nginx"

exit 0
