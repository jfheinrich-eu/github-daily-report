#!/usr/bin/env bash

builder="$(docker buildx ls 2>/dev/null | grep mybuilder)"
if [ -z "$builder" ]; then
    echo "Creating a new buildx builder named 'mybuilder'."
    docker run --privileged --rm tonistiigi/binfmt --install all
    docker buildx create --name mybuilder --use --driver docker-container
else
    echo "Using existing buildx builder: $builder"
    docker buildx use mybuilder
fi

docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --tag testbuild:buildx-latest \
    -f Dockerfile-daily-report .
