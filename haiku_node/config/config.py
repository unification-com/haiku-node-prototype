import json
import os, sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)


class UnificationConfig:

    def __init__(self):
        with open(parentdir + '/config/config.json') as f:
            self.conf = json.load(f)

    def get_conf(self):
        return self.conf

    def set_conf(self, key, val):
        self.conf[key] = val
        with open(parentdir + '/config/config.json', 'w') as f:
            json.dump(self.conf, f, indent=4)
