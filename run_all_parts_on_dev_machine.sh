#!/bin/bash

echo "This script launches all the components on a development machine"
echo "Note: Updated to use adminfrontend2"

tmux \
  new-session  "cd ./services ; ./run_app_developer.sh" \; \
  split-window "cd ./frontend2 ; quasar dev" \; \
  split-window "cd ./adminfrontend2 ; quasar dev" \; \
  select-layout main-horizontal \; \
  select-pane -t 0 \; \
  split-window "cd ./services ; ./insert_test_data.sh 4"
