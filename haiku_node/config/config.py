import json
import os
import inspect

import logging

log = logging.getLogger(__name__)


class UnificationConfig:

    def __init__(self):
        with open(self.parent_directory() + '/config/config.json') as f:
            self._conf = json.load(f)

    def __getitem__(self, item):
        return self._conf[item]

    def __setitem__(self, key, value):
        self._conf[key] = value
        with open(self.parent_directory() + '/config/config.json', 'w') as f:
            json.dump(self._conf, f, indent=4)

    def __repr__(self):
        return str(self._conf)

    def parent_directory(self):
        currentdir = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe())))
        return os.path.dirname(currentdir)
