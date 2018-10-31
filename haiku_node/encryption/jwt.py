import json
import time

from haiku_node.utils.utils import base64url_decode, base64url_encode, generate_nonce, json_encode, sha256
from haiku_node.blockchain_helpers.eos.eos_keys import UnifEosKey


class UnifJWT:

    __slots__ = ['jwt_header',
                 'jwt_payload',
                 'jwt_signature',
                 'jwt_header_enc',
                 'jwt_payload_enc',
                 'jwt_signature_enc',
                 'digest',
                 'digest_sha',
                 'jwt']

    def __init__(self, jwt=None):
        self.jwt = jwt

    def __generate_header(self):
        self.jwt_header = {
            "alg": "ES256K1",
            "typ": "jwt"
        }

    def __encode(self):
        self.jwt_header_enc = base64url_encode(json_encode(self.jwt_header))
        self.jwt_payload_enc = base64url_encode(json_encode(self.jwt_payload))
        self.digest = str(self.jwt_header_enc.decode()) + "." + str(self.jwt_payload_enc.decode())
        self.digest_sha = sha256(self.digest.encode('utf-8'))

    def generate(self, payload):
        payload['jti'] = generate_nonce()  # RFC 7519 4.1.7
        payload['iat'] = time.time()  # RFC 7519 4.1.6
        self.jwt_payload = payload
        self.__generate_header()
        self.__encode()

    def sign(self, private_key):
        eosk = UnifEosKey(private_key)
        self.jwt_signature = eosk.sign(self.digest_sha)
        self.jwt_signature_enc = base64url_encode(self.jwt_signature.encode('utf-8'))

        self.jwt = self.digest + "." + str(self.jwt_signature_enc.decode())

    def to_jwt(self):
        return self.jwt

    def get_issuer(self):
        if self.jwt is None:
            return None

        jwt_list = self.jwt.split('.')
        payload = json.loads(base64url_decode(jwt_list[1].encode('utf-8')))

        return payload['iss']

    def get_audience(self):
        if self.jwt is None:
            return None

        jwt_list = self.jwt.split('.')
        payload = json.loads(base64url_decode(jwt_list[1].encode('utf-8')))

        return payload['aud']

    def decode_jwt(self, public_key):
        if self.jwt is None:
            return {}

        jwt_list = self.jwt.split('.')
        eosk = UnifEosKey()
        payload = {}

        jwt_header_enc = jwt_list[0]
        jwt_payload_enc = jwt_list[1]
        jwt_signature_enc = jwt_list[2]

        digest = jwt_header_enc + "." + jwt_payload_enc

        digest_sha = sha256(digest.encode('utf-8'))

        jwt_signature = base64url_decode(jwt_signature_enc.encode('utf-8'))

        key_match = eosk.verify_pub_key(jwt_signature.decode(), digest_sha, public_key)

        if key_match:
            payload_str = base64url_decode(jwt_payload_enc.encode('utf-8'))
            payload = json.loads(payload_str)

        return payload
