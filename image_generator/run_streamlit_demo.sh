#!/bin/bash

PWD=$(pwd)

bash build_streamlit_docker.sh

docker run --rm -it --ipc=host \
  --runtime=nvidia \
  -p 80:8501 \
  -v "$PWD"/output/:/home/output/ \
  -v "$HOME"/.cache/huggingface/:/root/.cache/huggingface/ \
  neiroimaginarium-streamlit:latest
