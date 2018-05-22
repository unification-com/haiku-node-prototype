Haiku Node
==========

Setup with Docker
-----------------

Docker with Docker Compose is the simplest way to bring up this
software. This software has been tested on OSX against
`Docker 18.03.1-ce` and `Docker Compose 1.21.1`.

### Installing Docker on Ubuntu based systems

For full instructions on how to install Docker CE, see
<https://docs.docker.com/install/linux/docker-ce/ubuntu/>

Update apt

    sudo apt-get update

Install prerquisites

    sudo apt-get install apt-transport-https ca-certificates curl software-properties-common

Add Docker's GPG Key

    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

Add the Docker CE Repo

    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

Update apt

    sudo apt-get update

Install

    sudo apt-get install docker-ce

### Installing on Docker OSX

Docker for Mac can be obtained from here:
<https://docs.docker.com/docker-for-mac/>

### Bringing up the composition

From the root of the repository, build the containers with:

    make

create a volume to persist accounts:

    docker volume create --name keosd-data-volume

and finally bring the composition up:

    docker-compose --file Docker/docker-compose.yml up

