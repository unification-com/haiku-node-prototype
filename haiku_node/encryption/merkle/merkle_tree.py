import binascii
import hashlib


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
    def __init__(self, data: str, prefix_byte='0x00', position=None, level=1):
        # prefix byte to help prevent second preimage attack
        node = prefix_byte + data
        node_hash = sha256(sha256(node))
        self.hash = hex_to_bytes(node_hash)
        self.position = position  # l | r
        self.parent = None
        self.left_sibling = None
        self.right_sibling = None
        self.left_child = None
        self.right_child = None
        self.is_root = False

        if prefix_byte == '0x00':
            self.is_leaf = True
            self.level = 1
        else:
            self.is_leaf = False
            self.level = level

    def __setitem__(self, item, value):
        self.__dict__[item] = value

    def __getitem__(self, item):
        return self.__dict__[item]


class MerkleTree:

    def __init__(self):
        self.leaves = []
        self.num_levels = 0
        self.current_level = 1
        self.storage = {}
        self.last_leaf = None
        self.levels_prefix = '0x00'
        self.merkle_root = None

    def add_leaf(self, data: str):
        pos = self.__get_posistion(self.leaves)
        leaf = MerkleNode(data, position=pos)
        self.leaves.append(leaf)
        self.__store(leaf)
        self.last_leaf = leaf

    def grow_tree(self):
        if not self.leaves:
            raise MerkleException('No leaves found')

        # if odd number of leaves, duplicate last leaf
        if len(self.leaves) % 2 != 0:
            last_leaf = MerkleNode(bytes_to_hex(self.last_leaf.hash).decode(), position='r')
            self.__store(last_leaf)
            self.leaves.append(last_leaf)

        self.__calculate_num_levels()

        layer = self.leaves
        while len(layer) != 1:
            layer = self.__grow(layer)

        self.merkle_root = layer[0]
        self.__set_item_in_storage(bytes_to_hex(self.merkle_root.hash).decode(), 'is_root', True)

    def get_root(self):
        if self.merkle_root is not None:
            return bytes_to_hex(self.merkle_root.hash)

    def get_root_str(self):
        if self.merkle_root is not None:
            return bytes_to_hex(self.merkle_root.hash).decode()

    def __store(self, node):
        idx = bytes_to_hex(node.hash).decode()
        self.storage[idx] = node

    def __set_item_in_storage(self, idx, key, val):
        self.storage[idx][key] = val

    def __grow(self, nodes):
        new_level = []
        self.current_level = self.current_level + 1
        for i in range(0, len(nodes), 2):
            pos = self.__get_posistion(new_level)

            l_hash = bytes_to_hex(nodes[i].hash).decode()
            r_hash = bytes_to_hex(nodes[i + 1].hash).decode()

            new_node = MerkleNode(l_hash + r_hash,
                                  prefix_byte=self.levels_prefix,
                                  position=pos,
                                  level=self.current_level)

            new_node.left_child = nodes[i].hash
            new_node.right_child = nodes[i + 1].hash

            new_level.append(new_node)

            self.__store(new_node)
            self.__set_item_in_storage(l_hash, 'parent', new_node.hash)
            self.__set_item_in_storage(r_hash, 'parent', new_node.hash)

        return new_level

    def __get_posistion(self, obj):
        if len(obj) % 2 != 0:
            return 'r'
        else:
            return 'l'

    def __calculate_num_levels(self):
        num_nodes = len(self.leaves)
        if num_nodes > 0:
            self.num_levels = 1

            while num_nodes > 1:
                self.num_levels = self.num_levels + 1
                num_nodes = num_nodes / 2

        self.levels_prefix = f'0x0{self.num_levels}'
