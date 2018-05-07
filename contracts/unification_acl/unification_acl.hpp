/**
 *  @file unification_acl.hpp
 *  @copyright Paul Hodgson @ Unification Foundation
 */

#include <eosiolib/eosio.hpp>
#include <eosiolib/action.hpp>
#include <eosiolib/contract.hpp>
#include <eosiolib/print.hpp>

namespace UnificationFoundation {
    using namespace eosio;

    class unification_acl : public eosio::contract {
    public:
        explicit unification_acl(action_name self);

        //@abi action
        void grant(account_name user_account, account_name requesting_app);

        //@abi action
        void revoke(account_name user_account, account_name requesting_app);

        //abi action
        void check(account_name user_account, account_name requesting_app);

    private:

        void set_permission(account_name user_account, account_name requesting_app, int permission);

        //@abi table permission_record i64
        struct permission_record {
            uint64_t user_account; //user account ID
            uint8_t permission_granted; //whether or not user has granted access. 1 = true, 0 = false
                                        //bool type not yet supported in EOS

            uint64_t primary_key() const { return user_account; }

            EOSLIB_SERIALIZE(permission_record, (user_account)(permission_granted))

        };

        //https://github.com/EOSIO/eos/wiki/Persistence-API#multi-index-constructor
        typedef eosio::multi_index<N(unifacl), permission_record> unifperms;
    };

    EOSIO_ABI(unification_acl, (grant)(revoke)(check))
}