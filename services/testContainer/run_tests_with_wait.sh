#!/bin/bash

echo "Waiting to allow other container to start..."
sleep 5
echo "Wait over"
python3 -m pytest /ext_volume
exit $?
