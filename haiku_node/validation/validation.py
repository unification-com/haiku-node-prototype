from haiku_node.blockchain.eos.mother import UnificationMother
from haiku_node.network.eos import get_cleos, get_ipfs_client

"""
Validation class for a single REQUESTING app.
1) Loads UApp Data Smart Contract for THIS Haiku/App
2) Loads data from MOTHER for REQUESTING APP
3) Checks REQUESTING APP is valid according to MOTHER
"""


class UnificationAppScValidation:

    def __init__(self, eos_client, acl_contract, requesting_app):
        """
        :param requesting_app: the eos account name of the requesting app
        """
        self.__requesting_app = requesting_app
        self.__eosClient = eos_client
        self.__acl_contract = acl_contract
        self.__is_valid_app = False
        self.__is_valid_code = False

        self.__run()

    def valid_app(self):
        return self.__is_valid_app

    def valid_code(self):
        return self.__is_valid_code

    def valid(self):
        if self.__is_valid_app and self.__is_valid_code:
            return True
        else:
            return False

    def __check_req_app_valid(self):
        """
        Call the MOTHER Smart Contract, and check if the requesting_app is both
        a verified app, and that it's smart contract code is valid (by checking
        the code's hash).
        """

        um = UnificationMother(
            self.__eosClient, self.__requesting_app,
            get_cleos(), get_ipfs_client())
        self.__is_valid_app = um.valid_app()
        self.__is_valid_code = um.valid_code()

    def __run(self):
        self.__check_req_app_valid()


if __name__ == '__main__':
    print("Nope.")
