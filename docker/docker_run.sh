#!/bin/bash

NAME="ciroh-ngiab-python"
#docker build --platform linux/amd64 -t $NAME .
#docker build -t $NAME .

docker run -it \
       --name $NAME \
       -v "${PWD}/../":/shared/ \
       -v "${PWD}/../../NextGen/ngen-data/":/data/ \
       $NAME \
       bash
