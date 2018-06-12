/**
 *  @file unification_acl.hpp
 *  @copyright Paul Hodgson @ Unification Foundation
 */

#include <regex>
#include <eosiolib/eosio.hpp>

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
        void setschema(account_name schema_name, std::string schema);

        //@abi action
        void setsource(account_name source_name, std::string source_type);

        //@abi action
        void addhash(account_name schema_name, uint64_t schema_vers, uint64_t timestamp, std::string data_hash);

        //@abi action
        void setrewards(uint64_t user_amt, uint64_t app_amt);

    private:

        void set_permission(account_name user_account, account_name requesting_app, int permission);

        //@abi table permrecords i64
        struct permrecords {
            uint64_t user_account; //user account ID
            uint8_t permission_granted; //whether or not user has granted access. 1 = true, 0 = false
                                        //bool type not yet supported in EOS
            //https://github.com/EOSIO/eos/blob/15953cc1be7a4d4ff168d0235dbaba9464033b70/libraries/chain/contracts/abi_serializer.cpp#L56

            uint64_t primary_key() const { return user_account; }

            EOSLIB_SERIALIZE(permrecords, (user_account)(permission_granted))

        };

        //https://github.com/EOSIO/eos/wiki/Persistence-API#multi-index-constructor
        //eosio::multi_index<N([name_match_abi]), [name_match_struct]> [anything];
        typedef eosio::multi_index<N(permrecords), permrecords> unifperms;

        //@abi table dataschemas i64
        struct dataschemas {
            uint64_t pkey;
            uint64_t schema_name;
            account_name schema_name_str;
            uint64_t schema_vers;
            std::string schema;

            uint64_t primary_key() const { return pkey; }
            uint64_t by_name() const {return schema_name; }

            EOSLIB_SERIALIZE(dataschemas, (pkey)(schema_name)(schema_name_str)(schema_vers)(schema))
        };

        typedef eosio::multi_index<N(dataschemas), dataschemas,
                indexed_by< N(byname), const_mem_fun<dataschemas, uint64_t, &dataschemas::by_name> >
        > unifschemas;

        //@abi table datasources i64
        struct datasources {
            uint64_t pkey;
            uint64_t source_name;
            account_name source_name_str;
            std::string source_type; //"contract", "database", "file", do be decided
            uint64_t schema_id; //fkey link to data_schema
            uint64_t acl_contract_acc; //link to remote smart contract, if source = contract
            uint8_t in_use;

            uint64_t primary_key() const { return pkey; }
            uint64_t by_name() const { return source_name; }

            EOSLIB_SERIALIZE(datasources, (pkey)(source_name)(source_name_str)(source_type)(schema_id)(acl_contract_acc)(in_use))
        };

        typedef eosio::multi_index<N(datasources), datasources,
                indexed_by< N(byname), const_mem_fun<datasources, uint64_t, &datasources::by_name> >
        > unifsources;

        //@abi table datahashes i64
        struct datahashes {
            uint64_t pkey;
            uint64_t schema_id;
            uint64_t timestamp;
            std::string data_hash;

            uint64_t primary_key() const { return pkey; }
            uint64_t by_time() const { return timestamp; }

            EOSLIB_SERIALIZE(datahashes, (pkey)(schema_id)(timestamp)(data_hash))
        };

        typedef eosio::multi_index<N(datahashes), datahashes,
                indexed_by< N(bytime), const_mem_fun<datahashes, uint64_t, &datahashes::by_time> >
        > unifhashes;

        //@abi table undrewards i64
        struct undrewards {
            uint64_t pkey;
            uint64_t user_amt;
            uint64_t app_amt;

            uint64_t primary_key() const { return pkey; }

            EOSLIB_SERIALIZE(undrewards, (pkey)(user_amt)(app_amt))
        };

        typedef eosio::multi_index<N(undrewards), undrewards> unifrewards;

    };

    EOSIO_ABI(unification_acl, (grant)(revoke)(check)(setschema)(setsource)(addhash)(setrewards))
}
