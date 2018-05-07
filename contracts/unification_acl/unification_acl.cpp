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
}