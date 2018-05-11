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

        //@abi action
        void check(account_name user_account, account_name requesting_app);

        //@abi action
        void set_schema(std::string schema_name, std::string schema);

        //@abi action
        void set_source(std::string source_name, std::string source_type);

    private:

        void set_permission(account_name user_account, account_name requesting_app, int permission);

        //@abi table permission_record i64
        struct permission_record {
            uint64_t user_account; //user account ID
            uint8_t permission_granted; //whether or not user has granted access. 1 = true, 0 = false
                                        //bool type not yet supported in EOS
            //https://github.com/EOSIO/eos/blob/15953cc1be7a4d4ff168d0235dbaba9464033b70/libraries/chain/contracts/abi_serializer.cpp#L56

            uint64_t primary_key() const { return user_account; }

            EOSLIB_SERIALIZE(permission_record, (user_account)(permission_granted))

        };

        //https://github.com/EOSIO/eos/wiki/Persistence-API#multi-index-constructor
        typedef eosio::multi_index<N(unifacl), permission_record> unifperms;

        //@abi table data_schemas i64
        struct data_schemas {
            uint64_t pkey;
            uint64_t schema_name;
            std::string schema_name_str;
            uint64_t schema_vers;
            std::string schema;

            uint64_t primary_key() const { return pkey; }
            uint64_t by_name() const {return schema_name; }

            EOSLIB_SERIALIZE(data_schemas, (pkey)(schema_name)(schema_name_str)(schema_vers)(schema))
        };

        typedef eosio::multi_index<N(unifschemas), data_schemas,
                indexed_by< N(byname), const_mem_fun<data_schemas, uint64_t, &data_schemas::by_name> >
        > unifschemas;

        //@abi table data_sources i64
        struct data_sources {
            uint64_t pkey;
            uint64_t source_name;
            std::string source_name_str;
            std::string source_type; //"contract", "database", "file", do be decided
            uint64_t schema_id; //fkey link to data_schema
            uint64_t acl_contract_acc; //link to remote smart contract, if source = contract
            uint8_t in_use;

            uint64_t primary_key() const { return pkey; }
            uint64_t by_name() const {return source_name; }

            EOSLIB_SERIALIZE(data_sources, (pkey)(source_name)(source_name_str)(source_type)(schema_id)(acl_contract_acc)(in_use))
        };

        typedef eosio::multi_index<N(unifsources), data_sources,
                indexed_by< N(byname), const_mem_fun<data_sources, uint64_t, &data_sources::by_name> >
        > unifsources;

//        struct data_rewards {
//
//        };

    };

    EOSIO_ABI(unification_acl, (grant)(revoke)(check)(set_schema)(set_source))
}