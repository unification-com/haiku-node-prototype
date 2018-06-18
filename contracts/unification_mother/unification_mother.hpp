/**
 *  @file unification_acl.hpp
 *  @copyright Paul Hodgson @ Unification Foundation
 */

#include <eosiolib/eosio.hpp>

namespace UnificationFoundation {
    using namespace eosio;

    class unification_mother : public eosio::contract {
    public:
        explicit unification_mother(action_name self);

        //abi action
        void addnew(account_name acl_contract_acc,
                    std::string  schema_vers,
                    std::string acl_contract_hash,
                    std::string rpc_server_ip,
                    uint16_t rpc_server_port);

        //@abi action
        void validate(account_name acl_contract_acc);

        //@abi action
        void invalidate(account_name acl_contract_acc);

        //@abi action
        void isvalid(account_name acl_contract_acc);

        //@abi action
        void getapp(account_name acl_contract_acc);

    private:

        //@abi table validapps i64
        struct validapps {
            uint64_t acl_contract_acc;
            std::string schema_vers;
            std::string acl_contract_hash;
            std::string rpc_server_ip;
            uint16_t rpc_server_port;
            uint8_t is_valid;

            uint64_t primary_key() const { return acl_contract_acc; }

            EOSLIB_SERIALIZE(validapps, (acl_contract_acc)(schema_vers)(acl_contract_hash)(rpc_server_ip)(rpc_server_port)(is_valid))
        };

        //https://github.com/EOSIO/eos/wiki/Persistence-API#multi-index-constructor
        typedef eosio::multi_index<N(validapps), validapps> valapps;

        //@abi table binhashes i64
        struct binhashes {
            uint64_t pkey;
            uint64_t vnum;
            std::string vcode;
            uint64_t arch_id;
            std::string bin_hash;

            uint64_t primary_key() const { return pkey; }

            EOSLIB_SERIALIZE(binhashes, (pkey)(vnum)(vcode)(arch_id)(bin_hash))
        };

        typedef eosio::multi_index<N(binhashes), binhashes> bin_hashes;
    };

    EOSIO_ABI(unification_mother, (addnew)(validate)(invalidate)(isvalid)(getapp))
}