#!/bin/bash

TAG=latest

while [[ $# -gt 0 ]]; do
  case $1 in
    -t|--tag)
      TAG=$2
      shift
      shift
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
  esac
done

IMAGE_TAG="neiroimaginarium-streamlit:$TAG"

docker build --file Dockerfile-streamlit -t "$IMAGE_TAG" .
