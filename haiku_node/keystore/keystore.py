import json
import os, inspect

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)


class UnificationKeystore:

    def __init__(self, pw):
        self.__is_empty = True
        self.__encrypted_store = ""

        if len(pw) > 0:
            self.__fern = Fernet(str.encode(pw))
            self.__load_encrypted_keys()

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

        with open(parentdir + '/keystore/keys.store', 'wb') as f:
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

        keystore['enc_keys'][account_name][requesting_app] = key
        json_string = json.dumps(keystore)
        self.__encrypted_store = self.__fern.encrypt(str.encode(json_string))

        with open(parentdir + '/keystore/keys.store', 'wb') as f:
            f.write(self.__encrypted_store)
            self.__is_empty = False

    def __load_encrypted_keys(self):
        with open(parentdir + '/keystore/keys.store', 'rb') as f:
            self.__encrypted_store = f.read()
            if len(self.__encrypted_store) > 0:
                self.__is_empty = False


if __name__ == '__main__':
    print("Nope.")
