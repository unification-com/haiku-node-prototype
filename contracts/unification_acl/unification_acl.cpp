/**
 *  @file unification_acl.cpp
 *  @copyright Paul Hodgson @ Unification Foundation
 */

#include "unification_acl.hpp"

namespace UnificationFoundation {

    using namespace eosio;
    using eosio::indexed_by;
    using eosio::const_mem_fun;

/**
 *  @defgroup unification_acl3 Unification Access Control Contract
 *  @brief Defines user controlled access to data
 *
 *  @details
 *  Each app requesting data from THIS app is assigned a container in the contract,
 *  which can contain a growing list of users who have granted them access.
 *  Only users can call the grant/revoke functions to modify their status for a requesting app
 */

    unification_acl::unification_acl(action_name self) : contract(self) {}

    void unification_acl::grant(const account_name user_account,
                                const account_name requesting_app) {

        eosio::print(name{user_account}, " Called grant()");

        // make sure authorised by user. Only user can grant access to their data
        require_auth(user_account);

        set_permission(user_account,requesting_app,1);
    }

    void unification_acl::revoke(const account_name user_account,
                                 const account_name requesting_app) {

        eosio::print(name{user_account}, " Called revoke()");

        // make sure authorised by user. Only user can revoke access to their data
        require_auth(user_account);

        set_permission(user_account,requesting_app,0);

    }

    void unification_acl::check(const account_name user_account, const account_name requesting_app) {

        // code, scope. Scope = requesting app.
        unifperms perms(_self, requesting_app);

        int permission_granted = 0;

        auto itr = perms.find(user_account);
        if (itr != perms.end()) {
            permission_granted = itr->permission_granted;
        }

        //there doesn't currently seem to be a way to query the database for row(s), so temporary solution
        //just print out a JSON string.
        //All requesting app's permission statuses can be seen with command:
        //cleos get table [contract] [requesting_app] [table_name_in_abi]
        //e.g. cleos get table unif1 unif3 unifacl
        eosio::print("{\"user_account\":\"", name{user_account}, "\", \"requesting_app\":\"",name{requesting_app},"\",\"permission_granted\":",permission_granted,"}");

    }

    void unification_acl::set_permission(const account_name user_account, const account_name requesting_app, int permission) {

        // make sure authorised by user. Only user can revoke access to their data
        require_auth(user_account);

        // code, scope. Scope = requesting app.
        unifperms perms(_self, requesting_app);

        auto itr = perms.find(user_account);
        if (itr == perms.end()) {
            //no record for requesting app exists yet. Create one
            eosio::print(name{user_account}, " added ",permission," record for ", name{requesting_app});
            perms.emplace(_self /*payer*/, [&](auto &p_rec) {
                p_rec.user_account = user_account;
                p_rec.permission_granted = permission;
            });
        } else {
            //requesting app already has record for user. Update its user perms
            eosio::print(name{user_account}, " set access to ",permission," for ", name{requesting_app});
            perms.modify(itr, _self /*payer*/, [&](auto &p_rec) {
                p_rec.permission_granted = permission;
            });
        }
    }

    void unification_acl::set_schema(const std::string schema_name, const std::string schema) {
        eosio::print("set_schema()");

        require_auth(_self);
        eosio_assert(schema_name.length() <= 13, "schema_name must be <= 13 characters");
        eosio_assert(schema_name.find_first_not_of(".12345abcdefghijklmnopqrstuvwxyz") == std::string::npos,
                     "schema_name can only contain .12345abcdefghijklmnopqrstuvwxyz");

        unifschemas u_schema(_self, _self);

        const char *schema_name_cstr = schema_name.c_str();

        uint64_t vers = 0;
        uint64_t schema_name_int = eosio::string_to_name(schema_name_cstr);

        auto name_index = u_schema.template get_index<N(byname)>();
        auto itr = name_index.lower_bound(schema_name_int);

        for (; itr != name_index.end() && itr->schema_name == schema_name_int; ++itr) {
            vers = itr->schema_vers;
        }

        vers++;

        u_schema.emplace(_self, [&]( auto& s_rec ) {
            s_rec.pkey = u_schema.available_primary_key();
            s_rec.schema_name = schema_name_int;
            s_rec.schema_name_str = schema_name;
            s_rec.schema_vers = vers;
            s_rec.schema = schema;
        });

    }

    void unification_acl::set_source(const std::string source_name,
                                          const std::string source_type) {

        eosio::print("call set_data_source()");

        require_auth(_self);
        eosio_assert(source_name.length() <= 13, "source_name must be <= 13 characters");
        eosio_assert(source_name.find_first_not_of(".12345abcdefghijklmnopqrstuvwxyz") == std::string::npos,
                     "source_name can only contain .12345abcdefghijklmnopqrstuvwxyz");

        eosio_assert((source_type.compare("database") == 0
                      || source_type.compare("contract") == 0
                      || source_type.compare("file") == 0), "source_type must 'database', 'contract' or 'file'");

        bool update = false;
        uint64_t source_name_int = eosio::string_to_name(source_name.c_str());

        eosio_assert(source_name_int != _self,"Cannot add self as source");

        unifsources u_sources(_self, _self);
        auto source_name_index = u_sources.template get_index<N(byname)>();
        auto src_itr = source_name_index.find(source_name_int);
        if(src_itr != source_name_index.end()) {
            eosio::print("SOURCE FOUND");
            update = true;
        }

        uint64_t schema_pkey = 0;
        uint64_t acl_contract_acc_int = 0;
        unifschemas u_schema(_self, _self);
        auto schema_name_index = u_schema.template get_index<N(byname)>();

        if(source_type.compare("database") == 0 || source_type.compare("file") == 0) {

            eosio::print("source == database || file. ");
            auto sch_itr = schema_name_index.lower_bound(source_name_int);
            eosio_assert(sch_itr != schema_name_index.end(), "Schema not found");

            for (; sch_itr != schema_name_index.end() && sch_itr->schema_name == source_name_int; ++sch_itr) {
                schema_pkey = sch_itr->pkey;
            }


        } else if (source_type.compare("contract") == 0) {

            eosio::print("source == contract");
            auto sch_itr = schema_name_index.find(source_name_int);
            eosio_assert(sch_itr == schema_name_index.end(), "ACL Contract name already exists as a schema!");

            //TODO: Check target contract/account exixts
            acl_contract_acc_int = source_name_int;

        }

        if(update) {
            eosio::print("update");
            source_name_index.modify(src_itr, _self /*payer*/, [&](auto &s_rec) {
                s_rec.source_name = source_name_int;
                s_rec.source_name_str = source_name;
                s_rec.source_type = source_type;
                s_rec.schema_id = schema_pkey;
                s_rec.acl_contract_acc = acl_contract_acc_int;
                s_rec.in_use = 1;
            });
        } else {
            eosio::print("insert");
            u_sources.emplace(_self, [&]( auto& s_rec ) {
                s_rec.pkey = u_sources.available_primary_key();
                s_rec.source_name = source_name_int;
                s_rec.source_name_str = source_name;
                s_rec.source_type = source_type;
                s_rec.schema_id = schema_pkey;
                s_rec.acl_contract_acc = acl_contract_acc_int;
                s_rec.in_use = 1;
            });
        }

    }
}