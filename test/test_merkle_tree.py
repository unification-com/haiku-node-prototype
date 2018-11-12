import json
import pytest

from haiku_node.encryption.merkle.merkle_tree import MerkleTree, MerkleException

permission_json = {
  "user1": {
    "0": {
      "perms": "DataBlob,BlobSize",
      "p_nonce": "1595621598716744",
      "schema_id": "0",
      "consumer": "app1",
      "user": "user1",
      "b_nonce": "5215208105881115",
      "b_time": 1541500297.800053
    }
  },
  "user2": {
    "0": {
      "perms": "DataBlob",
      "p_nonce": "1917933605986945",
      "schema_id": "0",
      "consumer": "app1",
      "user": "user2",
      "b_nonce": "2322186965091853",
      "b_time": 1541500298.0310578
    }
  },
  "user3": {
    "0": {
      "perms": "BlobSize",
      "p_nonce": "0238349944470722",
      "schema_id": "0",
      "consumer": "app1",
      "user": "user3",
      "b_nonce": "5835621777972842",
      "b_time": 1541500298.2610202
    }
  },
  "user4": {
    "0": {
      "perms": "BlobSize",
      "p_nonce": "0238349944470723",
      "schema_id": "0",
      "consumer": "app1",
      "user": "user4",
      "b_nonce": "5835621777972842",
      "b_time": 1541500298.2610202
    }
  },
  "user5": {
    "0": {
      "perms": "BlobSize",
      "p_nonce": "0238349944470724",
      "schema_id": "0",
      "consumer": "app1",
      "user": "user5",
      "b_nonce": "5835621777972842",
      "b_time": 1541500298.2610202
    }
  },
  "user6": {
    "0": {
      "perms": "BlobSize",
      "p_nonce": "0238349944470725",
      "schema_id": "0",
      "consumer": "app1",
      "user": "user6",
      "b_nonce": "5835621777972842",
      "b_time": 1541500298.2610202
    }
  },
  "user7": {
    "0": {
      "perms": "BlobSize",
      "p_nonce": "0238349944470726",
      "schema_id": "0",
      "consumer": "app1",
      "user": "user7",
      "b_nonce": "5835621777972842",
      "b_time": 1541500298.2610202
    }
  },
  "user8": {
    "0": {
      "perms": "BlobSize",
      "p_nonce": "0238349944470727",
      "schema_id": "0",
      "consumer": "app1",
      "user": "user8",
      "b_nonce": "5835621777972842",
      "b_time": 1541500298.2610202
    }
  },
  "user9": {
    "0": {
      "perms": "BlobSize",
      "p_nonce": "0238349944470728",
      "schema_id": "0",
      "consumer": "app1",
      "user": "user9",
      "b_nonce": "5835621777972842",
      "b_time": 1541500298.2610202
    }
  }
}

permission_json_three = {
  "user1": {
    "0": {
      "perms": "DataBlob,BlobSize",
      "p_nonce": "1595621598716744",
      "schema_id": "0",
      "consumer": "app1",
      "user": "user1",
      "b_nonce": "5215208105881115",
      "b_time": 1541500297.800053
    }
  },
  "user2": {
    "0": {
      "perms": "DataBlob",
      "p_nonce": "1917933605986945",
      "schema_id": "0",
      "consumer": "app1",
      "user": "user2",
      "b_nonce": "2322186965091853",
      "b_time": 1541500298.0310578
    }
  },
  "user3": {
    "0": {
      "perms": "BlobSize",
      "p_nonce": "0238349944470722",
      "schema_id": "0",
      "consumer": "app1",
      "user": "user3",
      "b_nonce": "5835621777972842",
      "b_time": 1541500298.2610202
    }
  }
}


def test_grow_no_leaves_exception():
    tree = MerkleTree()

    with pytest.raises(MerkleException) as e:
        tree.grow_tree()
    assert 'No leaves found' in str(e.value)


def test_get_root_no_leaves_exception():
    tree = MerkleTree()

    with pytest.raises(MerkleException) as e:
        tree.get_root()
    assert 'No leaves found' in str(e.value)

    with pytest.raises(MerkleException) as e:
        tree.get_root_str()
    assert 'No leaves found' in str(e.value)


def test_get_root_not_grown_exception():
    tree = MerkleTree()

    for user, perm in permission_json.items():
        tree.add_leaf(json.dumps(perm))

    with pytest.raises(MerkleException) as e:
        tree.get_root()
    assert 'No tree stored. Grow from seed, or generate new tree' in str(e.value)

    with pytest.raises(MerkleException) as e:
        tree.get_root_str()
    assert 'No tree stored. Grow from seed, or generate new tree' in str(e.value)


def test_merkle_root():

    target_root = '26ad18e7cb43c6c1af2387039ede4c20366e7aa0b9d320f631c793c2bf255446'

    tree = MerkleTree()

    for user, perm in permission_json.items():
        tree.add_leaf(json.dumps(perm))

    tree.grow_tree()

    m_root = tree.get_root_str()

    assert m_root == target_root


def test_proof_not_hashed():
    target_root = '26ad18e7cb43c6c1af2387039ede4c20366e7aa0b9d320f631c793c2bf255446'

    tree = MerkleTree()

    for user, perm in permission_json.items():
        tree.add_leaf(json.dumps(perm))

    tree.grow_tree()

    requested_leaf = json.dumps(permission_json['user2'])

    proof = tree.get_proof(requested_leaf, is_hashed=False)

    is_good = tree.verify_leaf(requested_leaf, target_root,
                               proof, is_hashed=False)

    assert is_good

    requested_leaf = json.dumps(permission_json['user3'])
    proof_json = tree.get_proof(requested_leaf, is_hashed=False, as_json=True)

    is_good = tree.verify_leaf(requested_leaf,
                               target_root,
                               json.loads(proof_json), is_hashed=False)

    assert is_good


def test_proof_new_tree():
    target_root = '26ad18e7cb43c6c1af2387039ede4c20366e7aa0b9d320f631c793c2bf255446'

    tree = MerkleTree()

    for user, perm in permission_json.items():
        tree.add_leaf(json.dumps(perm))

    tree.grow_tree()

    requested_leaf = json.dumps(permission_json['user2'])

    proof_chain = tree.get_proof(requested_leaf, is_hashed=False)

    # simulate only having access to leaf, root and proof chain for leaf
    verify_tree = MerkleTree()

    is_good = verify_tree.verify_leaf(requested_leaf, target_root,
                                      proof_chain, is_hashed=False)

    assert is_good


def test_proof_all():
    tree = MerkleTree()

    for user, perm in permission_json.items():
        tree.add_leaf(json.dumps(perm))

    tree.grow_tree()

    for user, perm in permission_json.items():
        requested_leaf = json.dumps(permission_json[user])
        proof = tree.get_proof(requested_leaf, is_hashed=False)
        is_good = tree.verify_leaf(requested_leaf, tree.get_root_str(),
                                   proof, is_hashed=False)

        assert is_good


def test_load_from_seed():
    tree = MerkleTree()

    for user, perm in permission_json.items():
        tree.add_leaf(json.dumps(perm))

    tree.grow_tree()

    seed = tree.get_seed()
    original_root = tree.get_root_str()

    new_tree = MerkleTree(seed)
    new_tree.grow_tree()

    assert original_root == new_tree.get_root_str()


def test_load_from_seed_json():
    tree = MerkleTree()

    for user, perm in permission_json.items():
        tree.add_leaf(json.dumps(perm))

    tree.grow_tree()

    seed_json = tree.get_seed(as_json=True)
    original_root = tree.get_root_str()

    new_tree = MerkleTree(seed_json)

    assert original_root == new_tree.get_root_str()


def test_proof_from_new_seeded_tree():
    tree = MerkleTree()

    for user, perm in permission_json.items():
        tree.add_leaf(json.dumps(perm))

    tree.grow_tree()
    original_root = tree.get_root_str()

    seed_json = tree.get_seed(as_json=True)

    seeded_tree = MerkleTree(seed_json)

    proof_from_new = seeded_tree.get_proof(json.dumps(permission_json['user2']), is_hashed=False)

    is_good = seeded_tree.verify_leaf(json.dumps(permission_json['user2']),
                                      original_root,
                                      proof_from_new, is_hashed=False)

    assert is_good


def test_leaf_proof_mismatch():
    target_root = '26ad18e7cb43c6c1af2387039ede4c20366e7aa0b9d320f631c793c2bf255446'

    tree = MerkleTree()

    for user, perm in permission_json.items():
        tree.add_leaf(json.dumps(perm))

    tree.grow_tree()

    requested_leaf = json.dumps(permission_json['user2'])
    rubbish_leaf = json.dumps(permission_json['user3'])

    proof = tree.get_proof(requested_leaf, is_hashed=False)

    is_good = tree.verify_leaf(rubbish_leaf, target_root,
                               proof, is_hashed=False)

    assert not is_good


def test_three_leaves():
    tree = MerkleTree()
    for user, perm in permission_json_three.items():
        tree.add_leaf(json.dumps(perm))

    tree.grow_tree()

    for user, perm in permission_json_three.items():
        requested_leaf = json.dumps(permission_json_three[user])
        proof = tree.get_proof(requested_leaf, is_hashed=False)
        is_good = tree.verify_leaf(requested_leaf, tree.get_root_str(),
                                   proof, is_hashed=False)

        assert is_good
