Some instructions for compiling/testing the ACL smart contract on EOS installation. Assumes eosio is built/installed, and nodeos is running:

1) Create some wallets:
cleos wallet create -n user1
cleos wallet create -n user2
cleos wallet create -n user3
cleos wallet create -n app1
cleos wallet create -n app2
cleos wallet create -n app3

make a note of the passwords!

2) Unlock the wallets:

cleos wallet unlock -n user1
etc. - repeat for each wallet

3) Create a bunch of keys - one keypair for each wallet will do for testing:

cleos create key

repeat for each wallet created, so you have 6 public/private key pairs

4) Import PRIVATE keys into the wallets. For each wallet:

cleos wallet import -n user1 [private_key]

repeat for each wallet, using a different private key for each one

5) Create Accounts on blockchain:

cleos create account eosio user1 [user1_public_key] [user1_public_key]

repeat for user2, user3, app1 etc. Ensure correct public key is used (i.e. matches the private key imported into each wallet)

6) Copy unification_acl/unification_acl.cpp, .hpp and .abi to [download_dir_of_eos_git_]eos/contracts/unification_acl

7) cd [download_dir_of_eos_git]/eos/contracts/unification_acl

8) eosiocpp -o unification_acl.wast unification_acl.cpp

9) cd ..

10) cleos set contract app1 unification_acl unification_acl/unification_acl.wast unification_acl/unification_acl.abi -p app1

This will set the contract for the app1 account - so, this becomes the ACL Smart Contract for app1

11) Simulate user1 granting access for app2 to access data in app1:

cleos push action app1 grant '{"user_account":"user1", "requesting_app":"app2" }' -p user1

so, basically, it's calling the "grant" function on app1's ACL Smart Contract, telling it that user1 is granting access to app2. The "-p user1" is required, because only user1 can grant this access, and the Smart Contract code checks that user1 has signed this transaction and has the authority to do so.

You can also try changing "-p user1" to "-p user2" (leaving everything else in the command as it is), and the transaction should be rejected because user2 doesn;t have the authority to speak for user1.

12) Simulate user1 granting access for app3 to access data in app1:

cleos push action app1 grant '{"user_account":"user1", "requesting_app":"app3" }' -p user1

13) Simulate user2 denying access for app2 to access data in app1:

cleos push action app1 revoke '{"user_account":"user2", "requesting_app":"app2" }' -p user2

14) Query app1's permissions table for app2:

cleos get table app1 app2 unifacl

This basically grabs the table from app1's ACL Smart Contract, and filters it by permissions for app2. "unifacl" is just the name of the table within the Smart Contract

15) Query app1's permissions table for app3:

cleos get table app1 app3 unifacl

16) Check if app2 has access to user1's data:

cleos push action app1 check '{"user_account":"user1", "requesting_app":"app2" }'

There's currently no method for specific row queries in EOS Smart Contracts, so this is a temporary workaround, implementing the eosio::print method. I.e., unlike Ethereum/Solidity, there's currently no way to return values from a Smart Contract, and the cleos get table can only return rows for the given scope (in this smart contract, each requesting app has its own scope, and the user's account is used as the primary key within that scope). Hopefully, eventually, cleos get table will support primary key search too