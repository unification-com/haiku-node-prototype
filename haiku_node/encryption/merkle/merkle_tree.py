import binascii
import hashlib
import json

LEAF_PREFIX_BYTE = '0x00'


def sha256(data: str):
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def hex_to_bytes(hex_data: str):
    return bytearray.fromhex(hex_data)


def bytes_to_hex(bytes_data: bytearray):
    return binascii.hexlify(bytes_data)


class MerkleException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class MerkleNode:

    def __init__(self, data: str, prefix_byte=LEAF_PREFIX_BYTE, position=None, level=1):
        # prefix byte to help prevent second preimage attack
        node = prefix_byte + data
        node_hash = sha256(sha256(node))
        self.hash = hex_to_bytes(node_hash)
        self.position = position  # l | r
        self.parent = None
        self.sibling = None
        self.left_child = None
        self.right_child = None
        self.is_root = False

        if prefix_byte == LEAF_PREFIX_BYTE:
            self.is_leaf = True
            self.level = 1
        else:
            self.is_leaf = False
            self.level = level

    def to_string(self):
        parent = self.parent
        if parent:
            parent = bytes_to_hex(self.parent).decode()

        sibling = self.sibling
        if sibling:
            sibling = bytes_to_hex(self.sibling).decode()

        left_child = self.left_child
        if left_child:
            left_child = bytes_to_hex(self.left_child).decode()

        right_child = self.right_child
        if right_child:
            right_child = bytes_to_hex(self.right_child).decode()

        rank = 'Branch'
        if self.is_leaf:
            rank = 'Leaf'
        if self.is_root:
            rank = 'Root'

        return f'Hash: {bytes_to_hex(self.hash).decode()},\n' \
               f'Level: {self.level},\n' \
               f'Pos: {self.position},\n' \
               f'Parent: {parent},\n' \
               f'Sibling: {sibling},\n' \
               f'Left Child: {left_child},\n' \
               f'Right Child: {right_child},\n' \
               f'rank: {rank}\n'

    def __setitem__(self, item, value):
        self.__dict__[item] = value

    def __getitem__(self, item):
        return self.__dict__[item]


class MerkleTree:

    def __init__(self, storage_seed=None):
        self.leaves = []
        self.num_levels = 0
        self.current_level = 1
        self.storage = {}
        self.last_leaf = None
        self.levels_prefix = LEAF_PREFIX_BYTE
        self.merkle_root = None

        if storage_seed is not None:
            self.__grow_from_seed(storage_seed)

    def clear(self):
        self.leaves = []
        self.num_levels = 0
        self.current_level = 1
        self.storage = {}
        self.last_leaf = None
        self.levels_prefix = LEAF_PREFIX_BYTE
        self.merkle_root = None

    def add_leaf(self, data: str):
        pos = self.__determine_posistion(self.leaves)
        leaf = MerkleNode(data, position=pos)
        self.leaves.append(leaf)
        self.__store_node(leaf)
        self.last_leaf = leaf

    def grow_tree(self):
        if not self.leaves:
            raise MerkleException('No leaves found')

        self.__calculate_num_levels()

        layer = self.leaves
        while len(layer) != 1:
            layer = self.__grow(layer)

        self.merkle_root = layer[0]
        self.__set_node_in_storage(
            bytes_to_hex(self.merkle_root.hash).decode(),
            'is_root',
            True)

    def get_root(self):
        if self.merkle_root is not None:
            return bytes_to_hex(self.merkle_root.hash)

    def get_root_str(self):
        if self.merkle_root is not None:
            return bytes_to_hex(self.merkle_root.hash).decode()

    def get_proof(self, leaf_idx: str, is_hashed=True, as_json=False):

        if not self.storage:
            raise MerkleException("No tree stored. Grow from seed, or generate new tree")

        proof = {}
        root = bytes_to_hex(self.merkle_root.hash).decode()

        if not is_hashed:
            leaf = LEAF_PREFIX_BYTE + leaf_idx
            leaf_idx = sha256(sha256(leaf))

        if leaf_idx not in self.storage:
            raise MerkleException(f"Leaf ID {leaf_idx} not found in tree")

        leaf_node = self.storage[leaf_idx]
        if not leaf_node.is_leaf:
            raise MerkleException(f"Provided ID {leaf_idx} is not a leaf node")

        # proof['leaf'] = leaf_idx
        proof['leaf_pos'] = leaf_node.position
        proof['sibling'] = bytes_to_hex(leaf_node.sibling).decode()

        parent = bytes_to_hex(leaf_node.parent).decode()
        ancestors = []
        level_count = 0
        while parent != root and level_count <= self.num_levels:
            ancestor = {}
            parent_node = self.storage[parent]
            parent_sibling_hash = bytes_to_hex(parent_node.sibling).decode()
            ancestor['hash'] = parent_sibling_hash
            ancestor['pos'] = self.storage[parent_sibling_hash].position
            ancestors.append(ancestor)

            parent = bytes_to_hex(parent_node.parent).decode()
            level_count = level_count + 1

        proof['ancestors'] = ancestors

        if as_json:
            return json.dumps(proof)
        else:
            return proof

    def verify_leaf(self, leaf_idx: str, target_root: str, proof, is_hashed=True):
        if not is_hashed:
            leaf = LEAF_PREFIX_BYTE + leaf_idx
            leaf_idx = sha256(sha256(leaf))
            
        hash_prefix = f"0x0{len(proof['ancestors']) + 2}"

        if proof['leaf_pos'] == 'l':
            l_hash = leaf_idx
            r_hash = proof['sibling']
        else:
            l_hash = proof['sibling']
            r_hash = leaf_idx

        node_parent = MerkleNode(l_hash + r_hash,
                                 prefix_byte=hash_prefix)

        for ancestor in proof['ancestors']:
            if ancestor['pos'] == 'l':
                l_hash = ancestor['hash']
                r_hash = bytes_to_hex(node_parent.hash).decode()
            else:
                l_hash = bytes_to_hex(node_parent.hash).decode()
                r_hash = ancestor['hash']

            node_parent = MerkleNode(l_hash + r_hash,
                                     prefix_byte=hash_prefix)

        return target_root == bytes_to_hex(node_parent.hash).decode()

    def print_tree(self):
        for idx, node in self.storage.items():
            print(node.to_string())

    def get_seed(self, as_json=False):
        seed = {}
        for idx, node in self.storage.items():
            node_obj = vars(node)
            for key, val in node_obj.items():
                if isinstance(val, bytearray):
                    node_obj[key] = bytes_to_hex(val).decode()
            seed[idx] = vars(node)

        if as_json:
            return json.dumps(seed)
        else:
            return seed

    def __store_node(self, node):
        idx = bytes_to_hex(node.hash).decode()
        self.storage[idx] = node

    def __set_node_in_storage(self, idx, key, val):
        self.storage[idx][key] = val

    def __grow(self, nodes):
        new_level = []
        shift_node = None
        self.current_level = self.current_level + 1

        if len(nodes) % 2 != 0:
            shift_node = nodes.pop(-1)

        for i in range(0, len(nodes), 2):
            pos = self.__determine_posistion(new_level)

            l_hash = bytes_to_hex(nodes[i].hash).decode()
            r_hash = bytes_to_hex(nodes[i + 1].hash).decode()

            new_node = MerkleNode(l_hash + r_hash,
                                  prefix_byte=self.levels_prefix,
                                  position=pos,
                                  level=self.current_level)

            new_node['left_child'] = nodes[i].hash
            new_node['right_child'] = nodes[i + 1].hash

            new_level.append(new_node)

            self.__store_node(new_node)
            self.__set_node_in_storage(l_hash, 'parent', new_node.hash)
            self.__set_node_in_storage(r_hash, 'parent', new_node.hash)
            self.__set_node_in_storage(r_hash, 'sibling', hex_to_bytes(l_hash))
            self.__set_node_in_storage(l_hash, 'sibling', hex_to_bytes(r_hash))

        if shift_node is not None:
            if len(new_level) % 2 != 0:
                # new level size will be even after appending this. Set pos to 'r'
                shift_node['position'] = 'r'
            new_level.append(shift_node)

        return new_level

    def __grow_from_seed(self, storage_seed):

        to_convert = ['hash',
                      'parent',
                      'sibling',
                      'left_child',
                      'right_child']

        if isinstance(storage_seed, str):
            seed = json.loads(storage_seed)
        else:
            seed = storage_seed

        for idx, seed_node in seed.items():
            node = MerkleNode('0x00')

            for key, val in seed_node.items():
                if key in to_convert:
                    if seed_node[key] is not None:
                        node[key] = hex_to_bytes(seed_node[key])
                    else:
                        node[key] = None
                else:
                    node[key] = seed_node[key]

            if seed_node['is_leaf']:
                self.leaves.append(node)

            if seed_node['is_root']:
                self.merkle_root = node
                self.current_level = node.level

            self.__store_node(node)

        self.__calculate_num_levels()
        self.last_leaf = self.leaves[-1]

    def __determine_posistion(self, obj):
        if len(obj) % 2 != 0:
            return 'r'
        else:
            return 'l'

    def __calculate_num_levels(self):
        num_nodes = len(self.leaves)
        num_levels = 0
        if num_nodes > 0:
            num_levels = 1

            while num_nodes > 1:
                num_levels = num_levels + 1
                num_nodes = num_nodes / 2

        self.num_levels = num_levels
        self.levels_prefix = f'0x0{self.num_levels}'
