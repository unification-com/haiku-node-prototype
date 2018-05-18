FROM haiku

RUN apt-get update && \
    apt-get -y install \
        vim \
        telnet

RUN echo "cd /haiku/test; python systemtest.py probe" >> /root/.bash_history
RUN echo "alias ll='ls -la'" >> /root/.bashrc

WORKDIR /haiku/test
COPY test /haiku/test
