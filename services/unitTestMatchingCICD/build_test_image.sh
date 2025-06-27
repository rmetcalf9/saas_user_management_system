#!/bin/bash
set -e

BASE_IMAGE="python:3.10"
source ./vars.sh

cp ../src/requirements.txt ./src_requirements.txt
cp ../testContainer/requirements.txt ./container_requirements.txt

echo "🔧 Building test image with base image: $BASE_IMAGE and tag: $TAG"

docker build \
  --build-arg BASE_IMAGE="$BASE_IMAGE" \
  -f Dockerfile \
  -t "$TAG" \
  .
