FROM debian:latest

RUN apt-get update && \
    apt-get -y install \
        git \
        vim \
        telnet \
        make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
        libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev

RUN curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash && \
    /root/.pyenv/bin/pyenv install 3.6.0 && \
    ln -s /root/.pyenv/versions/3.6.0/bin/python3 /usr/bin/python && \
    ln -s /root/.pyenv/versions/3.6.0/bin/pip3 /usr/bin/pip

RUN mkdir /haiku
COPY requirements.txt /haiku

WORKDIR /haiku

RUN pip install -r requirements.txt && \
    ln -s /root/.pyenv/versions/3.6.0/bin/pytest /usr/bin/pytest

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV PYTHONPATH /haiku

EXPOSE 8050

RUN echo "haiku view app2 user1 data-1" >> /root/.bash_history && \
    echo "haiku fetch app2 user1 data-1" >> /root/.bash_history && \
    echo "alias ll='ls -la'" >> /root/.bashrc

COPY bin/haiku /usr/bin/haiku
COPY haiku_node /haiku/haiku_node
COPY test /haiku/test
COPY --from=unification-base /tmp/build/bin /opt/eosio/bin

CMD ["/haiku/test/bootstrap.sh"]
