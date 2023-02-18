#!/bin/bash
pip freeze > requirements.txt

# m1 libpg problem workaround
export DOCKER_DEFAULT_PLATFORM=linux/amd64

version='0.1-SNAPSHOT'

docker build . -t neuroginarium:$version
