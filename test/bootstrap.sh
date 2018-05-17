#!/usr/bin/env bash

cd /test; /root/.pyenv/versions/3.6.0/bin/python3 setup_test_host.py
cd /haiku; /root/.pyenv/versions/3.6.0/bin/python3 haiku_node/main.py
