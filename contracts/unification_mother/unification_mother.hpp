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
        void validate(account_name app_account,
                      account_name acl_contract,
                      account_name metadata_contract,
                      std::string app_name,
                      std::string desc,
                      std::string server_ip);

        //@abi action
        void invalidate(account_name app_account);

        //@abi action
        void is_valid(account_name app_account);

        //@abi action
        void get_app(account_name app_account);

    private:

        //@abi table permission_record i64
        struct valid_apps {
            uint64_t app_account;
            uint64_t acl_contract;
            uint64_t metadata_contract;
            std::string app_name;
            std::string desc;
            std::string server_ip;

            uint64_t primary_key() const { return app_account; }
            uint64_t by_acl() const { return acl_contract; }
            uint64_t by_metadata() const { return metadata_contract; }

            EOSLIB_SERIALIZE(valid_apps, (app_account)(acl_contract)(metadata_contract)(app_name)(desc)(server_ip))
        };

        //https://github.com/EOSIO/eos/wiki/Persistence-API#multi-index-constructor
        typedef eosio::multi_index<N(validapps), valid_apps,
                indexed_by< N(byacl), const_mem_fun<valid_apps, uint64_t, &valid_apps::by_acl> >,
                indexed_by< N(bymetadata), const_mem_fun<valid_apps, uint64_t, &valid_apps::by_metadata> >
        > validapps;
    };

    EOSIO_ABI(unification_mother, (validate)(invalidate)(is_valid)(get_app))
}