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
COPY external/ /haiku/external

WORKDIR /haiku

ENV PATH="/root/.pyenv/versions/3.6.0/bin:${PATH}"

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV PYTHONPATH /haiku

RUN pip install -r requirements.txt

EXPOSE 8050

RUN echo "haiku view app2 data-1" >> /root/.bash_history && \
    echo "haiku fetch app2 data-1" >> /root/.bash_history && \
    echo "haiku fetch app2 data-1 --user user1" >> /root/.bash_history && \
    echo "alias ll='ls -la'" >> /root/.bashrc

COPY bin/haiku /usr/bin/haiku
COPY haiku_node /haiku/haiku_node
COPY test /haiku/test
COPY --from=unification-base /tmp/build/bin /opt/eosio/bin

CMD ["/haiku/test/bootstrap.sh"]