#!/usr/bin/env bash

# Tested with Rancher Desktop 1.19.3 and Docker 28.1.1-rd
BUILDER_NAME="mybuilder"
docker run --privileged --rm tonistiigi/binfmt --install all >/dev/null

builder="$(docker buildx ls 2>/dev/null | grep $BUILDER_NAME)"
if [ -z "$builder" ]; then
    echo "Creating a new buildx builder named '$BUILDER_NAME'."
    docker buildx create --name $BUILDER_NAME --use --driver docker-container
else
    echo "Using existing buildx builder: $builder"
    docker buildx use $BUILDER_NAME
fi

if [ -z "$1" ] || [ "$1" = "multiarch" ]; then
    docker buildx build \
        --platform linux/amd64,linux/arm64 \
        --tag testbuild:buildx-latest \
        -f Dockerfile-daily-report .
fi

if [ -n "$1" ] && [ "$1" = "single" ]; then
    docker build --tag testbuild:docker-latest -f Dockerfile-daily-report .
fi
