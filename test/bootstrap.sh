#!/usr/bin/env bash

cd /haiku/test; python setup_test_host.py
cd /haiku; python haiku_node/main.py
