#!/usr/bin/bash



# build container

CONTAINER_NAME=telegraf_openweathermap
CONTAINER_TAG=latest


echo "docker build -t $CONTAINER_NAME:CONTAINER_TAG ."
docker build -t $CONTAINER_NAME:$CONTAINER_TAG .

