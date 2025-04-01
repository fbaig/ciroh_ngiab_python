#!/bin/bash

NAME="ngiab-ubuntu-2i2c"
docker build --platform linux/amd64 -t $NAME .

docker run -it \
       -v "${PWD}":/shared/ \
       -v "${PWD}/../../../NextGen/ngen-data":/data/ \
       -p 8888:8888 \
       $NAME \
       jupyter lab --ip 0.0.0.0 /shared
