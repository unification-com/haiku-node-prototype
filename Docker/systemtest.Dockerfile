FROM haiku

COPY --from=unification-base /tmp/build/bin /opt/eosio/bin
COPY --from=unification-contracts /eos/contracts/unification_uapp /eos/contracts/unification_uapp
COPY --from=unification-contracts /eos/contracts/unification_mother /eos/contracts/unification_mother
COPY --from=unification-contracts /eos/contracts/eosio.token /eos/contracts/eosio.token

COPY bin/haiku /usr/bin/haiku
COPY haiku_node /haiku/haiku_node
COPY test /haiku/test

RUN cd /haiku; find . -name "*.pyc" -exec rm -rf {} \; && \
    cd /haiku; export PYTHONPATH="."; pytest .

WORKDIR /haiku/test
