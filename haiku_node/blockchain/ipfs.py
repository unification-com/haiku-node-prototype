import ipfsapi

IPFS_HOST = 'ipfs'
IPFS_PORT = 5001


class IPFSDataStore:

    def __init__(self, host=IPFS_HOST, port=IPFS_PORT):
        self.api = ipfsapi.connect(host, port)

    def add_file(self, public_key_path):
        res = self.api.add(str(public_key_path))
        return res['Hash']

    def cat_file(self, file_hash):
        """
        #TODO: Why is the string substitution necessary?
        """
        f = self.api.cat(file_hash)
        return f.replace(b"\\n", b"\n")

    def add_json(self, json_str):
        ipfs_hash = self.api.add_json(json_str)
        return ipfs_hash

    def get_json(self, json_hash):
        return self.api.get_json(json_hash)
