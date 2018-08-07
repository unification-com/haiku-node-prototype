FROM debian:stretch-slim

RUN apt-get update && \
    apt-get -y install \
        less \
        wget \
        vim

WORKDIR /src

RUN wget https://dist.ipfs.io/go-ipfs/v0.4.15/go-ipfs_v0.4.15_linux-386.tar.gz && \
    tar xvfs go-ipfs_v0.4.15_linux-386.tar.gz && \
    cp /src/go-ipfs/ipfs /usr/local/bin

RUN echo "ipfs cat /ipfs/QmS4ustL54uo8FzR9455qaxZwuMiUhyvMcX9Ba8nUH4uVv/readme" >> /root/.bash_history && \
    echo "alias ll='ls -la'" >> /root/.bashrc

COPY Docker/ipfs/.ipfs /root/.ipfs
