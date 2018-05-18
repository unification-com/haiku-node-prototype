.DEFAULT_GOAL := all


all:
	docker build -f Docker/unification-base.Dockerfile -t unification-base .
	docker build -f Docker/unification-contracts.Dockerfile -t unification-contracts .
	docker build -f Docker/unification-node.Dockerfile -t unification-node .
	docker build -f Docker/haiku.Dockerfile -t haiku .
	docker build -f Docker/systemtest.Dockerfile -t systemtest .

haiku:
	docker build -f Docker/haiku.Dockerfile -t haiku .

systemtest:
	docker build -f Docker/systemtest.Dockerfile -t systemtest .

run:
	docker run -it systemtest /bin/bash

pytest:
	export PYTHONPATH="."; pytest test/test_asymmetric.py
