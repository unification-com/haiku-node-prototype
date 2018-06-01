#!/usr/bin/env bash

cd /haiku/test; python setup_test_host.py
cd /haiku; /usr/bin/haiku serve
