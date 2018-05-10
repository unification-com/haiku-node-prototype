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
        void set_schema(std::string schema);

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

        struct data_schema {
            uint64_t pkey;
            uint64_t schema_vers;
            std::string schema;

            uint64_t primary_key() const { return pkey; }
            uint64_t by_vers() const {return schema_vers; }

            EOSLIB_SERIALIZE(data_schema, (pkey)(schema_vers)(schema))
        };

        typedef eosio::multi_index<N(unifschema), data_schema,
                indexed_by< N(byvers), const_mem_fun<data_schema, uint64_t, &data_schema::by_vers> >
        > unifschema;

    };

    EOSIO_ABI(unification_acl, (grant)(revoke)(check)(set_schema))
}