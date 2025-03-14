#!/bin/bash

NAME="ngiab-ubuntu-wo-troute"
#docker buildx -t $NAME .
docker build --platform linux/amd64 -t $NAME .
#docker build -t $NAME .

# docker run -it \
#        -v "${PWD}":/shared/ \
#        $NAME \
#        bash
