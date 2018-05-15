.DEFAULT_GOAL := all


all:
	docker build -f Docker/unification-base.Dockerfile -t unification-base .
	docker build -f Docker/unification-contracts.Dockerfile -t unification-contracts .
	docker build -f Docker/unification-node.Dockerfile -t unification-node .
	docker build -f Docker/haiku.Dockerfile -t haiku .

haiku:
	docker build -f Docker/haiku.Dockerfile -t haiku .

run:
	docker run -it haiku /bin/bash

curl:
	curl --dump-header - -H "Content-Type: application/json" -X POST --data '{"client_id": "1", "access_token": "secret", "data_id": 1}' http://localhost:8850/data_request
