#!/bin/bash

PWD=$(pwd)

bash build_flask_docker.sh

docker run --rm -it --ipc=host \
  --runtime=nvidia \
  -p 80:80 \
  -v "$PWD"/output/:/home/output/ \
  -v "$HOME"/.cache/huggingface/:/root/.cache/huggingface/ \
  neiroimaginarium-flask:latest
