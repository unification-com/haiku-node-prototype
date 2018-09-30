FROM unification-base

COPY contracts/unification_uapp /eos/contracts/unification_uapp
COPY contracts/unification_mother /eos/contracts/unification_mother
COPY contracts/eosio.token /eos/contracts/eosio.token

WORKDIR /eos/contracts/unification_uapp
RUN /tmp/build/bin/eosiocpp -o unification_uapp.wast unification_uapp.cpp
RUN /tmp/build/bin/eosiocpp -g unification_uapp.abi unification_uapp.cpp

WORKDIR /eos/contracts/unification_mother
RUN /tmp/build/bin/eosiocpp -o unification_mother.wast unification_mother.cpp
RUN /tmp/build/bin/eosiocpp -g unification_mother.abi unification_mother.cpp

WORKDIR /eos/contracts/eosio.token
RUN /tmp/build/bin/eosiocpp -o eosio.token.wast eosio.token.cpp
RUN /tmp/build/bin/eosiocpp -g eosio.token.abi eosio.token.cpp

RUN echo "/tmp/build/bin/eosiocpp -o unification_uapp.wast unification_uapp.cpp" >> /root/.bash_history
RUN echo "/tmp/build/bin/eosiocpp -g unification_uapp.abi unification_uapp.cpp" >> /root/.bash_history
RUN echo "/tmp/build/bin/eosiocpp -o unification_mother.wast unification_mother.cpp" >> /root/.bash_history
RUN echo "/tmp/build/bin/eosiocpp -g unification_mother.abi unification_mother.cpp" >> /root/.bash_history
RUN echo "/tmp/build/bin/eosiocpp -o eosio.token.wast eosio.token.cpp" >> /root/.bash_history
RUN echo "/tmp/build/bin/eosiocpp -g eosio.token.abi eosio.token.cpp" >> /root/.bash_history
