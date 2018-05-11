Some instructions for compiling/testing the ACL smart contract on EOS installation. Assumes eosio is built/installed, and nodeos is running:

0) for brevity, run nodeos with the following plugins:
```
nodeos -e -p eosio --plugin eosio::wallet_api_plugin --plugin eosio::chain_api_plugin --plugin eosio::account_history_api_plugin
```

1) Create some wallets:
```
cleos wallet create -n user1
cleos wallet create -n user2
cleos wallet create -n user3
cleos wallet create -n app1
cleos wallet create -n app2
cleos wallet create -n app3
cleos wallet create -n unif.mother
```

make a note of the passwords!

2) Unlock the wallets:

```
cleos wallet unlock -n user1
```
etc. - repeat for each wallet

__Note: You will need to unlock the wallets each time you restart `nodeos`__

3) Create a bunch of keys - one keypair for each wallet will do for testing:
```
cleos create key
```

repeat for each wallet created, so you have 7 public/private key pairs

Make a note of the keys

4) Import PRIVATE keys into the wallets. For each wallet:

```
cleos wallet import -n user1 [private_key]
```

repeat for each wallet, using a different private key for each one

5) Create Accounts on blockchain:
```
cleos create account eosio user1 [user1_public_key] [user1_public_key]
```

repeat for user2, user3, app1 etc. Ensure correct public key is used (i.e. matches the private key imported into each wallet)

6) Copy unification_mother/unification_mother.cpp, .hpp and .abi to [download_dir_of_eos_git_]eos/contracts/unification_mother

7) Copy unification_acl/unification_acl.cpp, .hpp and .abi to [download_dir_of_eos_git_]eos/contracts/unification_acl

7) `cd [download_dir_of_eos_git]/eos/contracts/unification_mother`

8) `eosiocpp -o unification_mother.wast unification_mother.cpp`

9) `cd ../unification_acl`

10) `eosiocpp -o unification_acl.wast unification_acl.cpp`

11) `cd ..`

12) `cleos set contract app1 unification_acl unification_acl/unification_acl.wast unification_acl/unification_acl.abi -p app1`

This will set the contract for the app1 account - so, this becomes the ACL Smart Contract for app1

13) Repeat for app2, app3
```
cleos set contract app2 unification_acl unification_acl/unification_acl.wast unification_acl/unification_acl.abi -p app2
cleos set contract app3 unification_acl unification_acl/unification_acl.wast unification_acl/unification_acl.abi -p app3
```

14) Set the unification MOTHER smart contract
```
cleos set contract unif.mother unification_mother unification_mother/unification_mother.wast unification_mother/unification_mother.abi -p unif.mother
```

15) Set the (currently dummy) schema for each app:
```
cleos push action app1 set.schema '{"schema_name":"test1", "schema":"test1" }' -p app1
cleos push action app2 set.schema '{"schema_name":"test2", "schema":"test2" }' -p app2
cleos push action app3 set.schema '{"schema_name":"test3", "schema":"test3" }' -p app3
```

Schema tables can be retrieved:

```
cleos get table app1 app1 unifschemas
cleos get table app2 app2 unifschemas
cleos get table app3 app3 unifschemas
```

16) Set some sources. Note, for source_type = database, source_name must match an existing schema for the app
```
cleos push action app1 set.source '{"source_name":"test1", "source_type":"database"}' -p app1
cleos push action app2 set.source '{"source_name":"test2", "source_type":"database"}' -p app2
cleos push action app2 set.source '{"source_name":"app1", "source_type":"contract"}' -p app2
cleos push action app3 set.source '{"source_name":"test3", "source_type":"database"}' -p app3
```

Sources tables can be retrieved:

```
cleos get table app1 app1 unifsources
cleos get table app2 app2 unifsources
cleos get table app3 app3 unifsources
```

17) Get the code hash for each deplyed app contract (will probably be the same for each)

16) Get the code hash for each deployed app contract (will probably be the same for each)

```
cleos get code app1
cleos get code app2
cleos get code app3
```

18) Validate each app with MOTHER - acl_contract_hash value is from step #16. schema_vers is comman and colon separated list of schema_name:schema_vers, to represent latest valid schemas and versions for the app. Get from: `cleos get table app1 app1 unifschemas`

```
cleos push action unif.mother validate '{"acl_contract_acc":"app1", "schema_vers":"14605613945969442816:1", "acl_contract_hash": "6e89e37bb62e781ec301c9c0584f08ca8f2328e94f70bed2e589c358bff9b7ae", "server_ip": "127.0.0.1" }' -p unif.mother
cleos push action unif.mother validate '{"acl_contract_acc":"app2", "schema_vers":"14605614495725256704:1", "acl_contract_hash": "6e89e37bb62e781ec301c9c0584f08ca8f2328e94f70bed2e589c358bff9b7ae", "server_ip": "127.0.0.1" }' -p unif.mother
cleos push action unif.mother validate '{"acl_contract_acc":"app3", "schema_vers":"14605615045481070592:1", "acl_contract_hash": "6e89e37bb62e781ec301c9c0584f08ca8f2328e94f70bed2e589c358bff9b7ae", "server_ip": "127.0.0.1" }' -p unif.mother
```

19) Simulate user1 granting access for app2 to access data in app1:
```
cleos push action app1 grant '{"user_account":"user1", "requesting_app":"app2" }' -p user1
```

so, basically, it's calling the "grant" function on app1's ACL Smart Contract, telling it that user1 is granting access to app2. The "-p user1" is required, because only user1 can grant this access, and the Smart Contract code checks that user1 has signed this transaction and has the authority to do so.

You can also try changing "-p user1" to "-p user2" (leaving everything else in the command as it is), and the transaction should be rejected because user2 doesn't have the authority to speak for user1.

20) Simulate user1 granting access for app3 to access data in app1:
```
cleos push action app1 grant '{"user_account":"user1", "requesting_app":"app3" }' -p user1
```

21) Simulate user3 denying access for app2 to access data in app1:
```
cleos push action app1 revoke '{"user_account":"user3", "requesting_app":"app2" }' -p user3
```

22) Query app1's permissions table for app2:
```
cleos get table app1 app2 unifacl
```

This basically grabs the table from app1's ACL Smart Contract, and filters it by permissions for app2. "unifacl" is just the name of the table within the Smart Contract

23) Query app1's permissions table for app3:
```
cleos get table app1 app3 unifacl
```
24) Check if app2 has access to user1's data:
```
cleos push action app1 check '{"user_account":"user1", "requesting_app":"app2" }' -p app1
```
There's currently no method for specific row queries in EOS Smart Contracts, so this is a temporary workaround, implementing the eosio::print method. I.e., unlike Ethereum/Solidity, there's currently no way to return values from a Smart Contract, and the cleos get table can only return rows for the given scope (in this smart contract, each requesting app has its own scope, and the user's account is used as the primary key within that scope). Hopefully, eventually, cleos get table will support primary key search too

25) get app validation status/info from MOTHER:
```
cleos get table unif.mother unif.mother validapps
```
26) Can also run a validation test, from the git root:
```
python test/test_validation.py app2
python test/test_validation.py app3
```

config/config.json currently set up with "app1" as the data provider, so the above command is checking app2 and app3's validity/permissions as the data requesters.
