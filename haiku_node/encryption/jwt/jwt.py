import json
import time

from haiku_node.encryption.jwt.exceptions import *
from haiku_node.utils.utils import base64url_decode, base64url_encode, generate_nonce, json_encode, sha256
from haiku_node.blockchain_helpers.eos.eos_keys import UnifEosKey


INVALID_CHARACTERS = ['\n', '\t', '\r', ' ']
VALID_JOSE_KEYS = ['alg', 'typ']
SUPPORTED_JOSE_TYPES = ['jwt']
SUPPORTED_JOSE_ALGOS = ['ES256K1']


class UnifJWT:

    __slots__ = ['jwt_header',
                 'jwt_payload',
                 'jwt_signature',
                 'jwt_header_enc',
                 'jwt_payload_enc',
                 'jwt_signature_enc',
                 'jose_header_json',
                 'payload_json',
                 'digest',
                 'digest_sha',
                 'public_key',
                 'sig_valid',
                 'jwt']

    def __init__(self, jwt=None, public_key=None):
        self.jwt = jwt
        self.public_key = public_key
        if jwt is not None:
            if self.public_key is None:
                raise InvalidPublicKey("No public key given. Cannot validate signature")
            self.__verify_jwt()

    def __verify_jwt(self):
        # check has dot
        if '.' not in self.jwt:  # rfc7519 7.2: 1
            raise InvalidJWT("JWT Invalid: no period found")

        jwt_list = self.jwt.split('.')

        # check header
        self.__verify_jose_header(jwt_list)

        # validate JWS rfc7519 7.2: 7 and rfc7515 5.2
        if self.jwt.count(".") != 2:  # rfc7515 5.2: 1
            raise InvalidJWT("JWT Invalid: JWS Must contain exactly 2 periods")

        # verify payload
        self.__verify_jwt_payload(jwt_list)

        self.__verify_rfc7515(jwt_list)

        # validate signature
        self.__validate_signature()

        # set values
        self.jwt_payload = base64url_decode(self.jwt_payload_enc.encode('utf-8'))
        self.jwt_signature = base64url_decode(self.jwt_signature_enc.encode('utf-8'))
        self.payload_json = json.loads(self.jwt_payload)

    def __verify_jose_header(self, jwt_list):
        jwt_header_enc = jwt_list[0]  # rfc7519 7.2: 2

        if [c in jwt_header_enc for c in INVALID_CHARACTERS] == 1:  # rfc7519 7.2: 3
            raise InvalidJWT("Invalid Characters in JOSE header")

        jwt_header = base64url_decode(jwt_header_enc.encode('utf-8'))  # rfc7519 7.2: 3
        jose_header_json = json.loads(jwt_header)  # rfc7519 7.2: 4

        for k in jose_header_json.keys():  # rfc7519 7.2: 5
            if k not in VALID_JOSE_KEYS:
                raise InvalidJWT("Invalid keys in JOSE header JSON")

        self.jwt_header_enc = jwt_header_enc
        self.jwt_header = jwt_header
        self.jose_header_json = jose_header_json

    def __verify_jwt_payload(self, jwt_list):
        jwt_payload_enc = jwt_list[1]  # rfc7515 5.2: 6
        if [c in jwt_payload_enc for c in INVALID_CHARACTERS] == 1:  # rfc7515 5.2: 6
            raise InvalidJWT("Invalid Characters in JWS Payload")
        self.jwt_payload_enc = jwt_payload_enc

    def __verify_rfc7515(self, jwt_list):
        jwt_signature_enc = jwt_list[2]  # rfc7515 5.2: 7
        if [c in jwt_signature_enc for c in INVALID_CHARACTERS] == 1:  # rfc7515 5.2: 7
            raise InvalidJWT("Invalid Characters in JWS Signature")

        for k in VALID_JOSE_KEYS:
            if k not in self.jose_header_json.keys():  # rfc7515 5.2: 8
                raise InvalidJWT("Missing required keys in JOSE header JSON")

        self.jwt_signature_enc = jwt_signature_enc

    def __validate_signature(self):
        # rfc7515 5.2: 7
        eosk = UnifEosKey()
        digest = self.jwt_header_enc + "." + self.jwt_payload_enc
        digest_sha = sha256(digest.encode('utf-8'))
        jwt_signature = base64url_decode(self.jwt_signature_enc.encode('utf-8'))
        key_match = eosk.verify_pub_key(jwt_signature.decode(), digest_sha, self.public_key)

        self.sig_valid = key_match

        if not key_match:
            raise JWTSignatureMismatch("Invalid JWT: Signature mismatch")

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

    def get_payload(self):
        return self.payload_json

    def get_jose_header(self):
        return self.jose_header_json

    def get_signature(self):
        return self.jwt_signature

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
