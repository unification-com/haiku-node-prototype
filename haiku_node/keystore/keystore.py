import json
import os, inspect

from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


class UnificationKeystore:

    def __init__(self, pw, app_name=None):
        """
        :param pw: binary encoded password
        :param app_name: optional app specific keystore
        """
        self.__is_empty = True
        self.__encrypted_store = ""
        self.__app_name = app_name

        if len(pw) > 0:
            self.__fern = Fernet(pw)
            self.__load_encrypted_keys()

    def key_store_file(self):
        currentdir = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe())))
        parentdir = os.path.dirname(currentdir)

        if self.__app_name is None:
            return Path(parentdir + '/keystore/keys.store')
        else:
            return Path(parentdir + f"/keystore/keys-{ self.__app_name }.store")

    def get_rpc_auth_public_key(self):
        if not self.__is_empty:
            decrypted_store = self.__fern.decrypt(self.__encrypted_store)
            keystore = json.loads(decrypted_store)
            pem_key = str.encode(keystore['auth_key']['public_key'])
            return serialization.load_pem_public_key(
                pem_key,
                backend=default_backend())
        else:
            return False

    def get_rpc_auth_private_key(self):
        if not self.__is_empty:
            decrypted_store = self.__fern.decrypt(self.__encrypted_store)
            keystore = json.loads(decrypted_store)
            pem_key = str.encode(keystore['auth_key']['private_key'])
            return serialization.load_pem_private_key(
                pem_key,
                password=None,
                backend=default_backend())
        else:
            return False

    def set_rpc_auth_keys(self, pub, priv):
        keystore = {}

        if not self.__is_empty:
            decrypted_store = self.__fern.decrypt(self.__encrypted_store)
            keystore = json.loads(decrypted_store)

        if 'auth_key' not in keystore:
            keystore['auth_key'] = {}

        keystore['auth_key']['private_key'] = priv
        keystore['auth_key']['public_key'] = pub
        json_string = json.dumps(keystore)
        self.__encrypted_store = self.__fern.encrypt(str.encode(json_string))

        with self.key_store_file().open('wb') as f:
            f.write(self.__encrypted_store)
            self.__is_empty = False

    def get_encryption_key(self, account_name, requesting_app):
        if not self.__is_empty:
            decrypted_store = self.__fern.decrypt(self.__encrypted_store)
            keystore = json.loads(decrypted_store)
            return keystore['enc_keys'][account_name][requesting_app]
        else:
            return False

    def set_encryption_key(self, account_name, requesting_app, key):
        keystore = {}

        if not self.__is_empty:
            decrypted_store = self.__fern.decrypt(self.__encrypted_store)
            keystore = json.loads(decrypted_store)

        if 'enc_keys' not in keystore:
            keystore['enc_keys'] = {}
            keystore['enc_keys'][account_name] = {}
            keystore['enc_keys'][account_name][requesting_app] = ""

        if account_name not in keystore['enc_keys']:
            keystore['enc_keys'][account_name] = {}
            keystore['enc_keys'][account_name][requesting_app] = ""

        keystore['enc_keys'][account_name][requesting_app] = key
        json_string = json.dumps(keystore)
        self.__encrypted_store = self.__fern.encrypt(str.encode(json_string))

        with self.key_store_file().open('wb') as f:
            f.write(self.__encrypted_store)
            self.__is_empty = False

    def __load_encrypted_keys(self):
        with self.key_store_file().open('rb') as f:
            self.__encrypted_store = f.read()
            if len(self.__encrypted_store) > 0:
                self.__is_empty = False


if __name__ == '__main__':
    print("Nope.")
