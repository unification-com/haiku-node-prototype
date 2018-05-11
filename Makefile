.DEFAULT_GOAL := all


all:
	docker build -f Docker/unification-base.Dockerfile -t unification-base .
	docker build -f Docker/unification-contracts.Dockerfile -t unification-contracts .
	docker build -f Docker/unification-node.Dockerfile -t unification-node .

run:
	docker run -it unification-node /bin/bash
