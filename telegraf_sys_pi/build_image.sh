#!/usr/bin/bash



# build container

CONTAINER_NAME=telegraf_sys_pi
CONTAINER_TAG=latest
CONTAINER_TAG=0.6.5


echo "docker build -t $CONTAINER_NAME:$CONTAINER_TAG ."
docker build -t $CONTAINER_NAME:$CONTAINER_TAG .

