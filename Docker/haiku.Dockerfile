FROM debian:latest

RUN apt-get update && \
    apt-get -y install \
        #TODO: Remove git
        git \
        python3 \
        python3-pip

COPY haiku_node /haiku

WORKDIR /haiku

RUN pip3 install -r requirements.txt

EXPOSE 8050

CMD ["/usr/bin/python3", "rpc.py"]
