import base64
import json
import pytest

from haiku_node.blockchain_helpers.eos.eos_keys import UnifEosKey
from haiku_node.encryption.jwt.jwt import UnifJWT


def generate_eos_key_pair():
    """
    Generate EOS Key pair
    """
    eosk = UnifEosKey()
    private_key = eosk.to_wif()
    public_key = eosk.to_public()

    return private_key, public_key


def generate_jwt(payload, private_key):
    unif_jwt = UnifJWT()
    unif_jwt.generate(payload)
    unif_jwt.sign(private_key)

    jwt = unif_jwt.to_jwt()

    return jwt


def base64url_decode(input_str):
    rem = len(input_str) % 4
    if rem > 0:
        input_str += b'=' * (4 - rem)

    return base64.urlsafe_b64decode(input_str)


def base64url_encode(input_str):
    return base64.urlsafe_b64encode(input_str).replace(b'=', b'')


def json_encode(input_str):
    return json.dumps(input_str, separators=(',', ':')).encode('utf-8')


@pytest.mark.parametrize("payload", [
    {
        "user": "user2",
        "foo": "bar"
    },
    {
        "x": "y",
        "z": "a"
    },
    {
        "dfg": "123",
        "hjk": "456"
    }
])
def test_jwt(payload):

    private_key, public_key = generate_eos_key_pair()
    jwt = generate_jwt(payload, private_key)

    unif_jwt = UnifJWT(jwt)
    pl = unif_jwt.decode_jwt(public_key)

    assert not pl is False


@pytest.mark.parametrize("payload", [
    {
        "user": "user2",
        "foo": "bar"
    },
    {
        "x": "y",
        "z": "a"
    },
    {
        "dfg": "123",
        "hjk": "456"
    }
])
def test_jwt_key_mismatch(payload):

    private_key, public_key = generate_eos_key_pair()
    jwt = generate_jwt(payload, private_key)

    private_key2, public_key2 = generate_eos_key_pair()
    unif_jwt = UnifJWT(jwt)
    pl = unif_jwt.decode_jwt(public_key2)

    # should fail - key mismatch (decoded payload should be empty)
    assert not pl is True


@pytest.mark.parametrize("payload", [
    {
        "user": "user2",
        "foo": "bar"
    },
    {
        "x": "y",
        "z": "a"
    },
    {
        "dfg": "123",
        "hjk": "456"
    }
])
def test_jwt_payload_mismatch(payload):

    private_key, public_key = generate_eos_key_pair()
    jwt = generate_jwt(payload, private_key)

    # tamper with payload
    jwt_list = jwt.split('.')
    tampered_payload = json.loads(base64url_decode(jwt_list[1].encode('utf-8')))
    tampered_payload['nonce'] = 12345

    # repackage JWT
    jwt_tampered_payload_enc = base64url_encode(json_encode(tampered_payload))
    tampered_jwt = jwt_list[0] + "." + str(jwt_tampered_payload_enc.decode()) + "." + jwt_list[2]

    unif_jwt = UnifJWT(tampered_jwt)
    pl = unif_jwt.decode_jwt(public_key)

    # should fail - tampered payload (decoded payload should be empty)
    assert not pl is True
