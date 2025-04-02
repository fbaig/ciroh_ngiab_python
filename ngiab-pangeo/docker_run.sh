#!/bin/bash

NAME="ngiab-pangeo"
docker build --platform linux/amd64 -t $NAME .

docker run -it \
       -v "${PWD}":/shared/ \
       -p 8888:8888 \
       $NAME \
       jupyter lab --ip 0.0.0.0 /shared
