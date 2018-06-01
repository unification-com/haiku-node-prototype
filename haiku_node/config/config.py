import json
import os
import inspect

import logging

log = logging.getLogger(__name__)


class UnificationConfig:
    config_path = '/config/config.json'

    # Babel needs registered apps to render what the user permissions are
    registered_apps = ['app1', 'app2', 'app3']

    # Haiku server needs registered users to support bulk ingestion
    registered_users = ['user1', 'user2', 'user3']

    def __init__(self):
        with open(self.parent_directory() + self.config_path) as f:
            self.__conf = json.load(f)

    def __getitem__(self, item):
        return self.__conf.get(item)

    def __setitem__(self, key, value):
        self.__conf[key] = value
        with open(self.parent_directory() + self.config_path, 'w') as f:
            json.dump(self.__conf, f, indent=4)

    def __repr__(self):
        return str(self.__conf)

    def parent_directory(self):
        currentdir = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe())))
        return os.path.dirname(currentdir)
