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

    class unification_mother : public eosio::contract {
    public:
        explicit unification_mother(action_name self);

        //@abi action
        void validate(account_name acl_contract_acc,
                      std::string  schema_vers,
                      std::string acl_contract_hash,
                      std::string server_ip);

        //@abi action
        void invalidate(account_name acl_contract_acc);

        //@abi action
        void is_valid(account_name acl_contract_acc);

        //@abi action
        void get_app(account_name acl_contract_acc);

    private:

        //@abi table permission_record i64
        struct valid_apps {
            uint64_t acl_contract_acc;
            std::string schema_vers;
            std::string acl_contract_hash;
            std::string server_ip;
            uint8_t is_valid;

            uint64_t primary_key() const { return acl_contract_acc; }

            EOSLIB_SERIALIZE(valid_apps, (acl_contract_acc)(schema_vers)(acl_contract_hash)(server_ip)(is_valid))
        };

        //https://github.com/EOSIO/eos/wiki/Persistence-API#multi-index-constructor
        typedef eosio::multi_index<N(validapps), valid_apps> validapps;
    };

    EOSIO_ABI(unification_mother, (validate)(invalidate)(is_valid)(get_app))
}