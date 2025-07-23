#!/usr/bin/env bash

# Tested with Rancher Desktop 1.19.3 and Docker 28.1.1-rd

docker run --privileged --rm tonistiigi/binfmt --install all >/dev/null

builder="$(docker buildx ls 2>/dev/null | grep mybuilder)"
if [ -z "$builder" ]; then
    echo "Creating a new buildx builder named 'mybuilder'."
    docker buildx create --name mybuilder --use --driver docker-container
else
    echo "Using existing buildx builder: $builder"
    docker buildx use mybuilder
fi

docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --tag testbuild:buildx-latest \
    -f Dockerfile-daily-report .

docker build --tag testbuild:docker-latest -f Dockerfile-daily-report .
