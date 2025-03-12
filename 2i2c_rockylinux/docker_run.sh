#!/bin/bash

NAME="pangeo-2i2c"
#docker build -t $NAME .
#docker build --platform linux/amd64 -t $NAME .

##############
# To test Jupyter
##############
docker run -it \
       --rm \
       --volume "${PWD}/..":/shared \
       -p 8888:8888 \
       $NAME \
       jupyter lab --ip 0.0.0.0 /shared

##############
# To test container
##############
# docker run -it \
#        -v "${PWD}":/shared/ \
#        $NAME \
#        bash
