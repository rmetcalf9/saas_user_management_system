#!/bin/bash

#pyCharm will run in project root directory. Check if we are here and if so then change int oservices directory
if [ -d "./services" ]; then
  echo "Changing into services directory"
  cd ./services
fi

echo 'To test only highlighted with @wipd'
echo 'e.g. sudo ./continous_test.sh wip'

if [ $# -eq 0 ]; then
  until ack -f --python  ./src ./test | entr -d nosetests --rednose; do sleep 1; done
else
  if [ $# -eq 1 ]; then
    echo "Testing ${1}"
    until ack -f --python  ./src ./test | entr -d nosetests -a ${1} --rednose; do sleep 1; done
  else
    echo "Testing ${1} with verbose option (Single Run)"
    nosetests -v -a ${1} --rednose
  fi
fi
