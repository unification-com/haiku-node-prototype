import json
import os, sys, inspect
from cryptography.fernet import Fernet

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)


class UnificationKeystore:

    def __init__(self, pw):
        self.__is_empty = True
        self.__encrypted_store = ""

        if len(pw) > 0:
            self.__fern = Fernet(str.encode(pw))
            self.__load_encrypted_keys()

    def get_key(self, account_name, requesting_app):
        if not self.__is_empty:
            decrypted_store = self.__fern.decrypt(self.__encrypted_store)
            keystore = json.loads(decrypted_store)
            return keystore[account_name][requesting_app]
        else:
            return False

    def set_key(self, account_name, requesting_app, key):
        keystore = {}
        keystore[account_name] = {}
        keystore[account_name][requesting_app] = ""

        if not self.__is_empty:
            decrypted_store = self.__fern.decrypt(self.__encrypted_store)
            keystore = json.loads(decrypted_store)

        keystore[account_name][requesting_app] = key
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
