import json
import pytest

from haiku_node.encryption.merkle.merkle_tree import MerkleTree, MerkleException


def test_merkle_root():
    leaf_json = json.loads(
        '{"user1": {"0": {"perms": "DataBlob,BlobSize", "p_nonce": "1595621598716744", "p_sig": '
        '"SIG_K1_KYfGvUgQ7RLgKZiynjZBzZFPJyQEgNXKnDt7gKZXGy6sX1kNxpF3cSrWFceSEFK5uanK5mWU2fF2WnJtQWHJYD2KYsw7k8", '
        '"pub_key": "EOS6Nu8sazr6Pqr5LiWcTCKTgrKjnz7MCY3foSqkvsRHrueGry7sk", "schema_id": "0", "consumer": "app1", '
        '"user": "user1", "b_nonce": "5215208105881115", "b_time": 1541500297.800053}}, "user2": {"0": {"perms": '
        '"DataBlob", "p_nonce": "1917933605986945", "p_sig": '
        '"SIG_K1_KWWqBmzDebH9ENc1pQS6c1C9NPokT4r6NLZnbWy7nUiVmuzXAV9DjA43b3LL12w4yyUW7WYRA7Kp31BkcjaxDLu1cAoRka", '
        '"pub_key": "EOS5qVqrbHpD8KnLCCENDpSTL7K45tmNTzqdS92RV1fsx3SPbGSgA", "schema_id": "0", "consumer": "app1", '
        '"user": "user2", "b_nonce": "2322186965091853", "b_time": 1541500298.0310578}}, "user3": {"0": {"perms": '
        '"BlobSize", "p_nonce": "0238349944470721", "p_sig": '
        '"SIG_K1_KXNTfnzMvDPGnYLGRcnWrV3FsrGWBnaD2vH886jsT5UkVd9J2v82sp7BHDkzR2m6rJzGcLAvt5dQ3GCFscGauH1eY9MAix", '
        '"pub_key": "EOS61HzbDSsDVpbCjEaNw4hWEwVRyKtHW4rBcUAwbnk4NGB67Cu6V", "schema_id": "0", "consumer": "app1", '
        '"user": "user3", "b_nonce": "5835621777972842", "b_time": 1541500298.2610202}}, "user4": {"0": {"perms": '
        '"BlobSize", "p_nonce": "0238349944470721", "p_sig": '
        '"SIG_K1_KXNTfnzMvDPGnYLGRcnWrV3FsrGWBnaD2vH886jsT5UkVd9J2v82sp7BHDkzR2m6rJzGcLAvt5dQ3GCFscGauH1eY9MAix", '
        '"pub_key": "EOS61HzbDSsDVpbCjEaNw4hWEwVRyKtHW4rBcUAwbnk4NGB67Cu6V", "schema_id": "0", "consumer": "app1", '
        '"user": "user4", "b_nonce": "5835621777972842", "b_time": 1541500298.2610202}}, "user5": {"0": {"perms": '
        '"BlobSize", "p_nonce": "0238349944470721", "p_sig": '
        '"SIG_K1_KXNTfnzMvDPGnYLGRcnWrV3FsrGWBnaD2vH886jsT5UkVd9J2v82sp7BHDkzR2m6rJzGcLAvt5dQ3GCFscGauH1eY9MAix", '
        '"pub_key": "EOS61HzbDSsDVpbCjEaNw4hWEwVRyKtHW4rBcUAwbnk4NGB67Cu6V", "schema_id": "0", "consumer": "app1", '
        '"user": "user5", "b_nonce": "5835621777972842", "b_time": 1541500298.2610202}}, "user6": {"0": {"perms": '
        '"BlobSize", "p_nonce": "0238349944470721", "p_sig": '
        '"SIG_K1_KXNTfnzMvDPGnYLGRcnWrV3FsrGWBnaD2vH886jsT5UkVd9J2v82sp7BHDkzR2m6rJzGcLAvt5dQ3GCFscGauH1eY9MAix", '
        '"pub_key": "EOS61HzbDSsDVpbCjEaNw4hWEwVRyKtHW4rBcUAwbnk4NGB67Cu6V", "schema_id": "0", "consumer": "app1", '
        '"user": "user6", "b_nonce": "5835621777972842", "b_time": 1541500298.2610202}}, "user7": {"0": {"perms": '
        '"BlobSize", "p_nonce": "0238349944470721", "p_sig": '
        '"SIG_K1_KXNTfnzMvDPGnYLGRcnWrV3FsrGWBnaD2vH886jsT5UkVd9J2v82sp7BHDkzR2m6rJzGcLAvt5dQ3GCFscGauH1eY9MAix", '
        '"pub_key": "EOS61HzbDSsDVpbCjEaNw4hWEwVRyKtHW4rBcUAwbnk4NGB67Cu6V", "schema_id": "0", "consumer": "app1", '
        '"user": "user7", "b_nonce": "5835621777972842", "b_time": 1541500298.2610202}}}')

    target_root = '5d05eaac3902c7323bb996f25623aea201dbdc6985bb934f7b413acad51feea0'

    tree = MerkleTree()

    for user, perm in leaf_json.items():
        tree.add_leaf(json.dumps(perm))

    tree.grow_tree()

    m_root = tree.get_root_str()

    assert m_root == target_root
