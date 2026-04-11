#!/bin/bash

echo "This script launches all the components on a development machine"
echo "Note: Updated to use adminfrontend2"

if [[ ! -d ./services ]]; then
  echo "services not found - are you running from correct directory"
  exit 1
fi

if [[ ! -d ./frontend ]]; then
  echo "frontend not found - are you running from correct directory"
  exit 1
fi

if [[ ! -d ./adminfrontend ]]; then
  echo "frontend not found - are you running from correct directory"
  exit 1
fi


if [[ ! -f ./VERSION ]]; then
  echo "VERSION not found - are you running from correct directory"
  exit 1
fi


VER=$(cat VERSION)

echo "Overwiting hard coded codebaseversion file ():"
#must overwrite file not append so only single >
echo "/* eslint-disable */" > ./frontend/src/rjmversion.js
echo "export default { codebasever: 'run_all_parts_on_dev_machine_${VER}' }" >> ./frontend/src/rjmversion.js
echo "/* eslint-disable */" > ./adminfrontend/src/rjmversion.js
echo "export default { codebasever: 'run_all_parts_on_dev_machine_${VER}' }" >> ./adminfrontend/src/rjmversion.js


tmux \
  new-session  "cd ./services ; ./run_app_developer.sh" \; \
  split-window "cd ./frontend ; quasar dev" \; \
  split-window "cd ./adminfrontend ; quasar dev" \; \
  select-layout main-horizontal \; \
  select-pane -t 0 \; \
