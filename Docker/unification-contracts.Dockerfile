FROM unification-base

COPY contracts/unification_acl /eos/contracts/unification_acl
COPY contracts/unification_mother /eos/contracts/unification_mother

WORKDIR /eos/contracts/unification_acl
RUN /tmp/build/bin/eosiocpp -o unification_acl.wast unification_acl.cpp

WORKDIR /eos/contracts/unification_mother
RUN /tmp/build/bin/eosiocpp -o unification_mother.wast unification_mother.cpp

RUN echo "/tmp/build/bin/eosiocpp -o unification_acl.wast unification_acl.cpp" >> /root/.bash_history
RUN echo "/tmp/build/bin/eosiocpp -o unification_mother.wast unification_mother.cpp" >> /root/.bash_history
