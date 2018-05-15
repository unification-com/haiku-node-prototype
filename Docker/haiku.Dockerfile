FROM debian:latest

RUN apt-get update && \
    apt-get -y install \
        git \
        make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
        libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev

RUN curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
RUN /root/.pyenv/bin/pyenv install 3.6.0

RUN mkdir /haiku
COPY requirements.txt /haiku
COPY haiku_node /haiku/haiku_node

WORKDIR /haiku
RUN /root/.pyenv/versions/3.6.0/bin/pip3 install -r requirements.txt

WORKDIR /haiku/haiku_node
EXPOSE 8050

CMD ["/root/.pyenv/versions/3.6.0/bin/python3", "rpc.py"]
