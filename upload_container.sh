#!/bin/bash
aws ecr get-login-password --profile neuroginarium_dev --region eu-central-1 | docker login --username AWS --password-stdin 175070639038.dkr.ecr.eu-central-1.amazonaws.com

version='0.1-SNAPSHOT'

docker tag neuroginarium:$version 175070639038.dkr.ecr.eu-central-1.amazonaws.com/neuroginarium:$version

docker push 175070639038.dkr.ecr.eu-central-1.amazonaws.com/neuroginarium:$version
