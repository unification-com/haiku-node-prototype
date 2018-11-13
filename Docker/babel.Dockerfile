FROM debian:stretch-slim

RUN apt-get update && \
    apt-get -y install \
        git \
        vim \
        telnet \
        make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
        libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev

RUN curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash && \
    /root/.pyenv/bin/pyenv install 3.7.1

RUN mkdir /haiku
COPY requirements.txt /haiku
COPY external/ /haiku/external

WORKDIR /haiku

ENV PATH="/root/.pyenv/versions/3.7.1/bin:${PATH}"

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV PYTHONPATH /haiku

RUN pip install -r requirements.txt

RUN echo "babel permissions user1" >> /root/.bash_history && \
    echo "alias ll='ls -la'" >> /root/.bashrc

COPY bin/babel /usr/bin/babel
COPY bin/mother /usr/bin/mother
COPY haiku_node /haiku/haiku_node
COPY test /haiku/test
COPY --from=unification-base /tmp/build/bin /opt/eosio/bin
COPY test/data/babel_db/ /haiku/haiku_node/dbs
