.DEFAULT_GOAL := all


all:
	docker build -f Docker/unification-base.Dockerfile -t unification-base .
	docker build -f Docker/unification-contracts.Dockerfile -t unification-contracts .
	docker build -f Docker/unification-node.Dockerfile -t unification-node .
	docker build -f Docker/unification-keosd.Dockerfile -t unification-keosd .
	docker build -f Docker/haiku.Dockerfile -t haiku .
	docker build -f Docker/babel.Dockerfile -t babel .
	docker build -f Docker/ipfs/Dockerfile -t ipfs .
	docker build -f Docker/systemtest.Dockerfile -t systemtest .
	docker build -f Docker/mysql/Dockerfile -t mysql .

pytest:
	export PYTHONPATH="."; pytest .
