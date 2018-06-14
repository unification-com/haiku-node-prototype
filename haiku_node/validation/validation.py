from haiku_node.blockchain.mother import UnificationMother
from haiku_node.blockchain.acl import UnificationACL
from haiku_node.eosio_helpers import eosio_account


"""
Validation class for a single REQUESTING app.
1) Loads ACL/Meta Data Smart Contract for THIS Haiku/App
2) Loads data from MOTHER for REQUESTING APP
3) Checks REQUESTING APP is valid according to MOTHER
4) If REQUESTING APP is Valid, load permissions from THIS Haiku's ACL/Meta Data
    Smart Contract for the REQUESTING APP
"""


class UnificationAppScValidation:

    def __init__(self, eos_client, acl_contract, requesting_app,
                 get_perms=True):
        """
        :param requesting_app: the eos account name of the requesting app
        """
        self.__permission_rec_table = "permrecords"

        self.__requesting_app = requesting_app
        self.__eosClient = eos_client
        self.__acl_contract = acl_contract
        self.__get_perms = get_perms
        self.__is_valid_app = False
        self.__is_valid_code = False
        self.__granted = []
        self.__revoked = []

        self.__run()

    def app_has_user_permission(self, user_account):
        has_permission = False

        user_acc_uint64 = eosio_account.string_to_name(user_account)

        if user_acc_uint64 in self.__granted:
            has_permission = True

        return has_permission

    def users_granted(self):
        return self.__granted

    def users_revoked(self):
        return self.__revoked

    def valid_app(self):
        return self.__is_valid_app

    def valid_code(self):
        return self.__is_valid_code

    def valid(self):
        if self.__is_valid_app and self.__is_valid_code:
            return True
        else:
            return False

    def __get_app_permissions(self):
        """
        App checks it's own smart contract to see which users have granted
        permission to the REQUESTING APP to access it's data.
        """

        u_acl = UnificationACL(self.__eosClient, self.__acl_contract)
        self.__granted, self.__revoked = u_acl.get_perms_for_req_app(
            self.__requesting_app)

    def __check_req_app_valid(self):
        """
        Call the MOTHER Smart Contract, and check if the requesting_app is both
        a verified app, and that it's smart contract code is valid (by checking
        the code's hash).
        """

        um = UnificationMother(self.__eosClient, self.__requesting_app)
        self.__is_valid_app = um.valid_app()
        self.__is_valid_code = um.valid_code()

    def __run(self):
        self.__check_req_app_valid()
        if self.__is_valid_app and self.__is_valid_code and self.__get_perms:
            self.__get_app_permissions()
        else:
            self.__granted = []
            self.__revoked = []


if __name__ == '__main__':
    print("Nope.")
