# Smart Contracts

The following three Smart Contracts are used and deployed within the prototype:

## eosio.token

Deployed on the `unif.token` EOS account, and used to implement the 
UND token infrastructure within the Prototype.

## unification_acl

Deployed on each UApp's EOS account: `app1`, `app2`, and `app3`.

1. Stores metadata about data sources. Can only be modified by the 
app account on which the Smart Contract is deployed
2. Stores schema templates describing the data the app is making 
available within the Unification ecosystem. Can only be modified by the 
app account on which the Smart Contract is deployed
3. Stores user permission maps, describing which apps can access a 
users data within this app. Can only be modified by the user
4. Stores UND reward structures - i.e. how much this app will pay users/other
apps for data.

## unification_mother

Deployed on the `unif.mother` EOS account.

1. Stores a list of valid (and invalidated) apps within the Unification ecosystem.
Haiku Node always "calls MOTHER" to check that an app requesting its data is
valid.
2. Stores the code hash for each app's `unification_acl` Smart Contract
(at the time of validation). If the current deployed hash does not match
the hash stored in MOTHER, then data requests are rejected by Haiku Nodes.
3. Stores current valid schemas and versions for app data sources. If an app
modifies it's data schema template, or adds/removes sources, they won't
be "active" within the ecosystem until MOTHER is informed.

All data stored within the `unification_mother` Smart Contract can only
be updated by the `unif.mother` account.
