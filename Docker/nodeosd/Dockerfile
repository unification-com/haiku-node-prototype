FROM ubuntu:18.04

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y install openssl && rm -rf /var/lib/apt/lists/*
COPY --from=unification-base /usr/local/lib/* /usr/local/lib/
COPY --from=unification-base /tmp/build/bin /opt/eosio/bin
COPY --from=unification-base /tmp/build/contracts /contracts
COPY --from=unification-base /eos/Docker/config.ini /
COPY --from=unification-contracts /eos/contracts/unification_uapp /eos/contracts/unification_uapp
COPY --from=unification-contracts /eos/contracts/unification_mother /eos/contracts/unification_mother
COPY Docker/nodeosd/nodeosd.sh /opt/eosio/bin/nodeosd.sh
COPY Docker/nodeosd/config.ini /config.ini
ENV EOSIO_ROOT=/opt/eosio
RUN chmod +x /opt/eosio/bin/nodeosd.sh
ENV LD_LIBRARY_PATH /usr/local/lib
VOLUME /opt/eosio/bin/data-dir
ENV PATH /opt/eosio/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
