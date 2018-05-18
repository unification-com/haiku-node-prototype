import json
import os

from pathlib import Path

from haiku_node.keystore.keystore import UnificationKeystore


def password_for_app(app_name):
    """
    The key stores currently do not contain the public keys of the peer apps
    """
    current_directory = Path(os.path.abspath(__file__))
    par = current_directory.parent.parent.parent
    config = par / Path('test/data/system.json')

    contents = config.read_text()
    d = json.loads(contents)

    return d[app_name]['password']


def get_public_key(app_name):
    encoded_password = str.encode(password_for_app(app_name))
    ks = UnificationKeystore(encoded_password, app_name=app_name)
    return ks.get_rpc_auth_public_key()


def get_private_key(app_name):
    encoded_password = str.encode(password_for_app(app_name))
    ks = UnificationKeystore(encoded_password, app_name=app_name)
    return ks.get_rpc_auth_private_key()
