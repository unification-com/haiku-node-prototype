/**
 *  @file unification_mother.cpp
 *  @copyright Paul Hodgson @ Unification Foundation
 */

#include "unification_mother.hpp"

namespace UnificationFoundation {

    using namespace eosio;
    using eosio::indexed_by;
    using eosio::const_mem_fun;

/**
 *  @defgroup unification_mother MOTHER Contract
 *  @brief Contains validated apps in Unification system
 *
 *  @details
 *
 */

    unification_mother::unification_mother(action_name self) : contract(self) {}

    void unification_mother::addnew(const account_name acl_contract_acc,
                                      const std::string  schema_vers,
                                      const std::string acl_contract_hash,
                                      const std::string rpc_server_ip,
                                      const uint16_t rpc_server_port) {

        eosio::print(name{_self}, " Called validate()");

        // make sure authorised by unification
        eosio::require_auth(_self);

        valapps v_apps(_self, _self);

        auto itr = v_apps.find(acl_contract_acc);

        if (itr == v_apps.end()) {
            //no record for app exists yet. Create one
            v_apps.emplace(_self /*payer*/, [&](auto &v_rec) {
                v_rec.acl_contract_acc = acl_contract_acc;
                v_rec.schema_vers = schema_vers;
                v_rec.acl_contract_hash = acl_contract_hash;
                v_rec.rpc_server_ip = rpc_server_ip;
                v_rec.rpc_server_port = rpc_server_port;
                v_rec.is_valid = 1;
            });
        } else {
            //requesting app already has record. Update
            v_apps.modify(itr, _self /*payer*/, [&](auto &v_rec) {
                v_rec.schema_vers = schema_vers;
                v_rec.acl_contract_hash = acl_contract_hash;
                v_rec.rpc_server_ip = rpc_server_ip;
                v_rec.rpc_server_port = rpc_server_port;
                v_rec.is_valid = 1;
            });
        }

    }

    void unification_mother::validate(const account_name acl_contract_acc) {

        // make sure authorised by unification
        require_auth(_self);

        valapps v_apps(_self, _self);

        // verify already exist
        auto itr = v_apps.find(acl_contract_acc);
        eosio_assert(itr != v_apps.end(), "Address for account not found");

        v_apps.modify(itr, _self /*payer*/, [&](auto &v_rec) {
            v_rec.is_valid = 1;
        });

    }

    void unification_mother::invalidate(const account_name acl_contract_acc) {

        // make sure authorised by unification
        require_auth(_self);

        valapps v_apps(_self, _self);

        // verify already exist
        auto itr = v_apps.find(acl_contract_acc);
        eosio_assert(itr != v_apps.end(), "Address for account not found");

        v_apps.modify(itr, _self /*payer*/, [&](auto &v_rec) {
            v_rec.is_valid = 0;
        });

    }

    void unification_mother::isvalid(const account_name acl_contract_acc) {

        // code, scope. Scope = requesting app.
        valapps v_apps(_self, _self);

        int is_valid = 0;

        auto itr = v_apps.find(acl_contract_acc);
        if (itr != v_apps.end()) {
            is_valid = itr->is_valid;
        }

        eosio::print("{\"app_account\":\"", name{acl_contract_acc}, "\", \"is_valid\":",is_valid,"}");

    }

    void unification_mother::getapp(const account_name acl_contract_acc) {

        // code, scope. Scope = requesting app.
        valapps v_apps(_self, _self);

        auto itr = v_apps.find(acl_contract_acc);
        if (itr != v_apps.end()) {

        }

        //eosio::print("{\"app_account\":\"", name{app_account}, "\", \"is_valid\":",is_valid,"}");

    }

}