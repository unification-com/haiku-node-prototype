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

    void unification_mother::validate(const account_name app_account,
                                      const account_name acl_contract,
                                      const account_name metadata_contract,
                                      const std::string app_name,
                                      const std::string desc,
                                      const std::string server_ip) {

        eosio::print(name{_self}, " Called grant()");

        // make sure authorised by unification
        require_auth(_self);

        validapps v_apps(_self, _self);

        auto itr = v_apps.find(app_account);

        if (itr == v_apps.end()) {
            //no record for app exists yet. Create one
            v_apps.emplace(_self /*payer*/, [&](auto &v_rec) {
                v_rec.app_account = app_account;
                v_rec.acl_contract = acl_contract;
                v_rec.metadata_contract = metadata_contract;
                v_rec.app_name = app_name;
                v_rec.desc = desc;
                v_rec.server_ip = server_ip;
            });
        } else {
            //requesting app already has record. Update
            v_apps.modify(itr, _self /*payer*/, [&](auto &v_rec) {
                v_rec.app_account = app_account;
                v_rec.acl_contract = acl_contract;
                v_rec.metadata_contract = metadata_contract;
                v_rec.app_name = app_name;
                v_rec.desc = desc;
                v_rec.server_ip = server_ip;
            });
        }

    }

    void unification_mother::invalidate(const account_name app_account) {

        // make sure authorised by unification
        require_auth(_self);

        validapps v_apps(_self, _self);

        // verify already exist
        auto itr = v_apps.find(app_account);
        eosio_assert(itr != v_apps.end(), "Address for account not found");

        v_apps.erase( itr );

    }

    void unification_mother::is_valid(const account_name app_account) {

        // code, scope. Scope = requesting app.
        validapps v_apps(_self, _self);

        int is_valid = 0;

        auto itr = v_apps.find(app_account);
        if (itr != v_apps.end()) {
            is_valid = 1;
        }

        eosio::print("{\"app_account\":\"", name{app_account}, "\", \"is_valid\":",is_valid,"}");

    }

    void unification_mother::get_app(const account_name app_account) {

        // code, scope. Scope = requesting app.
        validapps v_apps(_self, _self);

        auto itr = v_apps.find(app_account);
        if (itr != v_apps.end()) {

        }

        //eosio::print("{\"app_account\":\"", name{app_account}, "\", \"is_valid\":",is_valid,"}");

    }

}