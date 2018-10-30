import pytest

from haiku_node.blockchain_helpers.eos_keys import UnifEosKey
from haiku_node.encryption.jwt import UnifJWT


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
