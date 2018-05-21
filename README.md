haiku-node-prototype
====================

pip install -r requirements.txt

Docker
======

Docker with Docker Compose is the simplest way to bring up this
software. On OSX, both are available from Docker CE. This software has
been tested with `Docker 18.03.1-ce` and `Docker Compose 1.21.1`.

From the root of the repository, build the containers with:

    make

Create a volume to persist accounts:

    docker volume create --name keosd-data-volume

and finally bring the composition up:

    docker-compose --file Docker/docker-compose.yml up

