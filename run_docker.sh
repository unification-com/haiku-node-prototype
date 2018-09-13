#!/bin/bash

export HAIKU_ROOT=$(pwd)

echo "Clean  Docker orphans"

docker-compose --file Docker/docker-compose.yml down --remove-orphans &
PID=$!
wait $PID

echo "Run make"
make &
PID=$!
wait $PID

docker-compose --file Docker/docker-compose.yml up
