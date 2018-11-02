import base64
import hashlib
import json
import random


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def generate_nonce(length=8):
    return ''.join([str(random.randint(0, 9)) for i in range(length)])


def json_encode(input_str):
    return json.dumps(input_str, separators=(',', ':')).encode('utf-8')


def base64url_decode(input_str):
    rem = len(input_str) % 4

    if rem > 0:
        input_str += b'=' * (4 - rem)

    return base64.urlsafe_b64decode(input_str)


def base64url_encode(input_str):
    return base64.urlsafe_b64encode(input_str).replace(b'=', b'')


def generate_perm_digest_sha(perms, schema_id, nonce, consumer):
    perm_digest = perms + str(schema_id) + consumer + str(nonce)

    return sha256(perm_digest.encode('utf-8'))
