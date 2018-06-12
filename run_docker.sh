#!/bin/bash

docker-compose --file Docker/docker-compose.yml down --remove-orphans
make
docker-compose --file Docker/docker-compose.yml up
