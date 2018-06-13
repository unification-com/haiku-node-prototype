Haiku Node
==========

Setup with Docker
-----------------

Docker with Docker Compose is the simplest way to bring up this
software. On OSX and Linux, both are available from Docker CE. This
software has been tested against `Docker 18.03.1-ce` and
`Docker Compose 1.21.1`.

### Installing Docker on Ubuntu based systems

For full instructions on how to install Docker CE, see
<https://docs.docker.com/install/linux/docker-ce/ubuntu/>

Update apt

    sudo apt-get update

Install prerequisites

    sudo apt-get install apt-transport-https ca-certificates curl software-properties-common

Add Docker's GPG Key

    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

Add the Docker CE Repo

    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

Update apt

    sudo apt-get update

Install

    sudo apt-get install docker-ce

Additional step - you may need to add your user to the docker group,
then log out/in:

    sudo adduser [username] docker

Install the latest Docker Compose. For full instructions, see
<https://docs.docker.com/compose/install/>

Download the latest version

    sudo curl -L https://github.com/docker/compose/releases/download/1.21.2/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose

Make executable

    sudo chmod +x /usr/local/bin/docker-compose

Test

    docker-compose --version

should output

    docker-compose version 1.21.2, build 1719ceb

### Installing on Docker OSX

Docker for Mac can be obtained from here:
<https://docs.docker.com/docker-for-mac/>

### Bringing up the composition

From the root of the repository, build the containers with:

    make

and finally bring the composition up:

    docker-compose --file Docker/docker-compose.yml up

The Babel and Haiku CLI
-----------------------

In this prototype implementation, there are two command line tools
simulating the behaivour of the Haiku server, and the end user. Their
names are respectively "haiku" and "babel". We are going to demonstrate
App3 consuming data from App1 and App2.

Once the Docker composition is up, and the system tests have run, open a
bash process on the `babel` container:

    docker exec -it babel /bin/bash

### Observing App Info

From the babel container, we can observe the data sources that App3 has
configured:

    babel sources app3

We can see one database source, and two contract sources.

### Observing Permissions

Currently there are three users in the ecosystem. We can observe the
permissions a user has granted to the apps to access data.

    babel permissions user1

### Fetching Data

From the third Haiku node, we can attempt to access the data (despite
the user not having granted access). Open a bash process on the third
Haiku node:

    docker exec -it haiku-app3 /bin/bash

and attempt to fetch the data:

    haiku fetch app2 user1 data-1

The request should be denied.

### Changing Permissions

`user1` can grant App3 permission to access it's data on App1 via Babel,
with it's EOS account password. On the `babel` container, execute:

    babel grant app2 app3 user1 PW5KZ2g5KuwVw2QhjNGn9aBbiSGsf3uq5HTigWohM6P7H767kw3dx

Now, fetching the data should be permitted:

    haiku fetch app2 user1 data-1

Currently, the data is stored locally, and cannot be viewed directly
because it is encrypted using App3's public RSA key. Via Babel, we can
decrypt the data using App3's private RSA key and view it:

    haiku view app2 user1 data-1

### Checking balances

Fetch the UND balance for an app/user:

    cleos get currency balance unif.token [account_name] UND

E.g.

    cleos get currency balance unif.token user1 UND

Transfer UNDs using babel

    babel transfer [from] [to] [amount] [wallet_password]
    babel transfer user1 user2 1 PW5KZ2g5KuwVw2QhjNGn9aBbiSGsf3uq5HTigWohM6P7H767kw3dx

Check UND balance

    babel balance [account_name] [wallet_password]
    babel balance user1 PW5KZ2g5KuwVw2QhjNGn9aBbiSGsf3uq5HTigWohM6P7H767kw3dx

Contribution Guidelines
-----------------------

### Regenerating Static Resources

Often, when the contents of `demo_config.json` is changed, the lookup
databases need to be regenerated, and commited. The simplest way to do
this is:

Bring the composition up and open a bash process in the `systemtest`
container:

    docker exec -it systemtest /bin/bash

Regenerate the lookup tables:

    python create_lookups.py

This should have deleted the current ones, and created new ones.

On the host machine, in the root of the repo, download the lookup
databases:

    docker cp systemtest:/haiku/test/data/lookups/app1.unification_lookup.db test/data/lookups/app1.unification_lookup.db
    docker cp systemtest:/haiku/test/data/lookups/app2.unification_lookup.db test/data/lookups/app2.unification_lookup.db
    docker cp systemtest:/haiku/test/data/lookups/app3.unification_lookup.db test/data/lookups/app3.unification_lookup.db

Finally, commit these with the reason for the change.
