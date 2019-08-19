#!/bin/bash

echo 'To test only highlighted with @wipd'
echo 'e.g. sudo ./continous_test.sh wip'

if [ $# -eq 0 ]; then
  until ack -f --python  ./src ./test | entr -d nosetests --rednose ./test; do sleep 1; done
else
  echo "Testing ${1}"
  until ack -f --python  ./src ./test | entr -d nosetests -a ${1} --rednose ./test; do sleep 1; done
fi
