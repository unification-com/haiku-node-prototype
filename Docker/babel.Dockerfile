FROM debian:stretch-slim

RUN apt-get update && \
    apt-get -y install \
        git \
        vim \
        telnet \
        make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
        libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev

RUN curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash && \
    /root/.pyenv/bin/pyenv install 3.6.0

RUN mkdir /haiku
COPY requirements.txt /haiku

WORKDIR /haiku

ENV PATH="/root/.pyenv/versions/3.6.0/bin:${PATH}"

RUN pip install -r requirements.txt

COPY --from=unification-base /tmp/build/bin /opt/eosio/bin

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV PYTHONPATH /haiku

RUN echo "babel permissions user1" >> /root/.bash_history && \
    echo "babel grant app2 app3 user1 PW5KZ2g5KuwVw2QhjNGn9aBbiSGsf3uq5HTigWohM6P7H767kw3dx" >> /root/.bash_history && \
    echo "babel revoke app1 app2 user3 PW5KfhcoCs5yV7wLTWWh97fZbf9jshHZL7vD9tQARfpCGVnDyA95t" >> /root/.bash_history && \
    echo "alias ll='ls -la'" >> /root/.bashrc

COPY bin/babel /usr/bin/babel
COPY bin/mother /usr/bin/mother
COPY haiku_node /haiku/haiku_node
COPY test /haiku/test
COPY --from=unification-base /tmp/build/bin /opt/eosio/bin

