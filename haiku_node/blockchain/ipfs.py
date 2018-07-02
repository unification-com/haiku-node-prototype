import ipfsapi

IPFS_HOST = 'ipfs'
IPFS_PORT = 5001


class IPFSDataStore:

    def __init__(self):
        self.api = ipfsapi.connect(IPFS_HOST, IPFS_PORT)

    def add_file(self, public_key_path):
        res = self.api.add(str(public_key_path))
        return res['Hash']

    def cat_file(self, file_hash):
        """
        #TODO: Why is the string substitution necessary?
        """
        f = self.api.cat(file_hash)
        return f.replace(b"\\n", b"\n")
