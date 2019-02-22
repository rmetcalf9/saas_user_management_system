#!/bin/bash

echo "This script launches all the components on a development machine"

tmux \
  new-session  "cd ./services ; ./run_app_developer.sh" \; \
  split-window "cd ./frontend ; quasar dev" \; \
  split-window "cd ./adminfrontend ; quasar dev" \; \
  select-layout main-horizontal \; \
  select-pane -t 0 \; \
  split-window "cd ./services ; ./insert_test_data.sh 4"




