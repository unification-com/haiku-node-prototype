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

curl:
	curl --insecure --dump-header - -H "Content-Type: application/json" -X POST --data '{"eos_account_name": "app2", "signature": "T3V5TNUofIhjPyr+cjOWD94N1q5Vwqozb+M7xvxqNiMOsb8fnUF9cWrOPZ1v/qirZ0AD9QehYo/7yGtE1iQXLU/KBe8XJmKISphDGwD5zh2wTjo/83e/GZerrBFhsUbuWye886lW+Q+WWJuLJ6M7PlpZlZgm23hWhyb6Kudf+z42vVrSL0IF1MP05n/tBGJ2ASw44wWrqC+oMIya6phAcx0iZ+4TSUmsePaEP+0XGV8hOKL/RIuEwvXkPWNzbiLZo44aU5uNokngRGJb9qqYoiEX313OT7vOiZK2Vjy9jtW0kKqOGBRzr6uSA2Mu2iQwFZsv6U1UKiShGKJy8P0djA==", "body": "request body"}' https://localhost:8850/data_request

pytest:
	export PYTHONPATH="."; pytest test/test_asymmetric.py
