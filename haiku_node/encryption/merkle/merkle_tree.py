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
    def __init__(self, data: str, prefix_byte='0x00'):
        # prefix byte to help prevent second preimage attack
        node = prefix_byte + data
        node_hash = sha256(sha256(node))
        self.hash = hex_to_bytes(node_hash)
        self.left = None
        self.right = None


class MerkleTree:

    def __init__(self):
        self.leaves = []
        self.levels = 0
        self.layers = []
        self.last_leaf = None
        self.levels_prefix = '0x00'
        self.merkle_root = None

    def add_leaf(self, data: str):
        leaf = MerkleNode(data)
        self.leaves.append(leaf)
        self.last_leaf = leaf

    def grow_tree(self):
        if not self.leaves:
            raise MerkleException('No leaves found')

        # if odd number of leaves, duplicate last leaf
        if len(self.leaves) % 2 != 0:
            self.leaves.append(self.last_leaf)

        self.__calculate_num_levels()

        layer = self.leaves
        self.layers.append(layer)
        while len(layer) != 1:
            layer = self.__grow(layer)
            self.layers.append(layer)

        self.merkle_root = layer[0]

    def get_root(self):
        if self.merkle_root is not None:
            return bytes_to_hex(self.merkle_root.hash)

    def get_root_str(self):
        if self.merkle_root is not None:
            return bytes_to_hex(self.merkle_root.hash).decode()

    def __grow(self, nodes):
        new_level = []
        for i in range(0, len(nodes), 2):
            new_node = MerkleNode(
                bytes_to_hex(nodes[i].hash).decode() + bytes_to_hex(nodes[i + 1].hash).decode(),
                self.levels_prefix)

            new_level.append(new_node)
        return new_level

    def __calculate_num_levels(self):
        num_nodes = len(self.leaves)
        if num_nodes > 0:
            self.levels = 1

            while num_nodes > 1:
                self.levels = self.levels + 1
                num_nodes = num_nodes / 2

        self.levels_prefix = f'0x0{self.levels}'
