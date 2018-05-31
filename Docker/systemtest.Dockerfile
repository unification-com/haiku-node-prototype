FROM haiku

COPY --from=unification-base /tmp/build/bin /opt/eosio/bin
COPY --from=unification-contracts /eos/contracts/unification_acl /eos/contracts/unification_acl
COPY --from=unification-contracts /eos/contracts/unification_mother /eos/contracts/unification_mother

RUN echo "cd /haiku/test; python systemtest.py probe" >> /root/.bash_history

COPY haiku_node /haiku/haiku_node
COPY test /haiku/test

RUN cd /haiku; find . -name "*.pyc" -exec rm -rf {} \; && \
    cd /haiku; export PYTHONPATH="."; pytest .

WORKDIR /haiku/test
