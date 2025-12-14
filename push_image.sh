#!/bin/bash


ENV=.env

if [ -f "$ENV" ]; then
    . $ENV
else
    IMAGE_NAME=$(basename `pwd`)
    CONTAINER_TAG=0.6.5
    REPO_USER_USER=juharov
fi

TAG=$CONTAINER_TAG

docker login

echo
echo "docker image push $REPO_USER_USER/${IMAGE_NAME}:${TAG}"
docker image push $REPO_USER_USER/${IMAGE_NAME}:${TAG}


if ! [[ ${TAG} =~ image ]]; then
    echo "docker image push $REPO_USER_USER/${IMAGE_NAME}:latest"
    docker image push $REPO_USER_USER/${IMAGE_NAME}:latest
else
    echo "  for the dev TAG '${TAG}' we do not push a 'latest'"
fi

