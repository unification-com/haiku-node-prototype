import base64
import json
import random
import time

from eospy.utils import sha256
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

    def __generate_nonce(self, length=8):
        """Generate pseudorandom number."""
        return ''.join([str(random.randint(0, 9)) for i in range(length)])

    def __generate_header(self):
        self.jwt_header = {
            "alg": "ES256K1",
            "typ": "jwt"
        }

    def __encode(self):
        self.jwt_header_enc = self.__base64url_encode(self.__json_encode(self.jwt_header))
        self.jwt_payload_enc = self.__base64url_encode(self.__json_encode(self.jwt_payload))
        self.digest = str(self.jwt_header_enc.decode()) + "." + str(self.jwt_payload_enc.decode())
        self.digest_sha = sha256(self.digest.encode('utf-8'))

    def __json_encode(self, input_str):
        return json.dumps(input_str, separators=(',', ':')).encode('utf-8')

    def __base64url_decode(self, input_str):
        rem = len(input_str) % 4

        if rem > 0:
            input_str += b'=' * (4 - rem)

        return base64.urlsafe_b64decode(input_str)

    def __base64url_encode(self, input_str):
        return base64.urlsafe_b64encode(input_str).replace(b'=', b'')

    def generate(self, payload):
        payload['jti'] = self.__generate_nonce()  # RFC 7519 4.1.7
        payload['iat'] = time.time()  # RFC 7519 4.1.6
        self.jwt_payload = payload
        self.__generate_header()
        self.__encode()

    def sign(self, private_key):
        eosk = UnifEosKey(private_key)
        self.jwt_signature = eosk.sign(self.digest_sha)
        self.jwt_signature_enc = self.__base64url_encode(self.jwt_signature.encode('utf-8'))

        self.jwt = self.digest + "." + str(self.jwt_signature_enc.decode())

    def to_jwt(self):
        return self.jwt

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

        jwt_signature = self.__base64url_decode(jwt_signature_enc.encode('utf-8'))

        key_match = eosk.verify_pub_key(jwt_signature.decode(), digest_sha, public_key)

        if key_match:
            payload_str = self.__base64url_decode(jwt_payload_enc.encode('utf-8'))
            payload = json.loads(payload_str)

        return payload
