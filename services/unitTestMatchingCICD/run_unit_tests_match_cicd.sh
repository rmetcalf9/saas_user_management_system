#!/bin/bash
set -e

source ./vars.sh

echo "🚀 Running tests from image: $TAG"
docker run -it --rm \
  -v "$(pwd)/..":/curdir \
  -w /curdir \
  -e SKIPSQLALCHEMYTESTS=Y \
  "$TAG" \
  bash -c "python3 -m pytest ./test"
