FROM unification-base

COPY contracts/unification_acl /eos/contracts/unification_acl
COPY contracts/unification_mother /eos/contracts/unification_mother
COPY contracts/eosio.token /eos/contracts/eosio.token

#WORKDIR /eos/contracts/unification_acl
#RUN /tmp/build/bin/eosiocpp -o unification_acl.wast unification_acl.cpp
#RUN /tmp/build/bin/eosiocpp -g unification_acl.abi unification_acl.cpp

#WORKDIR /eos/contracts/unification_mother
#RUN /tmp/build/bin/eosiocpp -o unification_mother.wast unification_mother.cpp
#RUN /tmp/build/bin/eosiocpp -g unification_mother.abi unification_mother.cpp

#WORKDIR /eos/contracts/eosio.token
#RUN /tmp/build/bin/eosiocpp -o eosio.token.wast eosio.token.cpp

#RUN echo "/tmp/build/bin/eosiocpp -o unification_acl.wast unification_acl.cpp" >> /root/.bash_history
#RUN echo "/tmp/build/bin/eosiocpp -g unification_acl.abi unification_acl.cpp" >> /root/.bash_history
#RUN echo "/tmp/build/bin/eosiocpp -o unification_mother.wast unification_mother.cpp" >> /root/.bash_history
#RUN echo "/tmp/build/bin/eosiocpp -g unification_mother.abi unification_mother.cpp" >> /root/.bash_history
