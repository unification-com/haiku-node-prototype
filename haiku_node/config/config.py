import json
import os
import inspect

from pathlib import Path

import logging

log = logging.getLogger(__name__)


class UnificationConfig:
    config_path = '/config/config.json'

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

    def demo_app_config(self):
        """
        TODO: This is technical debt. The app_config section in the demo_config
        needs to be merged into config.json, and served here
        :return:
        """

        log.warning('Remove this technical debt')
        parent_directory = Path(self.parent_directory())
        p = parent_directory.parent
        demo_config = p / Path('test/data/demo_config.json')
        d = json.loads(demo_config.read_text())
        return d['demo_apps'][self['acl_contract']]
