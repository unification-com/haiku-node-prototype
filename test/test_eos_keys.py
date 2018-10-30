# encoding: utf-8

import pytest

from eospy.utils import sha256
from haiku_node.blockchain_helpers.eos_keys import UnifEosKey


def generate_eos_key_pair():
    """
    Generate EOS Key pair
    """
    eosk = UnifEosKey()
    private_key = eosk.to_wif()
    public_key = eosk.to_public()

    return private_key, public_key


def sign_message(private_key, message):
    eosk = UnifEosKey(private_key)

    digest_sha = sha256(message.encode('utf-8'))

    signed_msg = eosk.sign(digest_sha)

    return signed_msg, digest_sha


@pytest.mark.parametrize("message", [
    "bar",
    "x",
    "'¡ooʇ ןnɟǝsn sı uʍop-ǝpısdn unicode ¡ooʇ ןnɟǝsn sı uʍop-ǝpısdn"
])
def test_sign_and_verify_pub_key(message):

    private_key, public_key = generate_eos_key_pair()
    signed_msg, digest_sha = sign_message(private_key, message)

    eosk = UnifEosKey()

    # Check public key against signature
    assert eosk.verify_pub_key(signed_msg, digest_sha, public_key) is True


@pytest.mark.parametrize("message", [
    "bar",
    "x",
    "'¡ooʇ ןnɟǝsn sı uʍop-ǝpısdn unicode ¡ooʇ ןnɟǝsn sı uʍop-ǝpısdn"
])
def test_sign_and_verify_change_pub_key(message):

    private_key, public_key = generate_eos_key_pair()
    signed_msg, digest_sha = sign_message(private_key, message)

    eosk = UnifEosKey()
    private_key2, public_key2 = generate_eos_key_pair()

    # Should fail, since public key doesn't match signed message
    assert eosk.verify_pub_key(signed_msg, digest_sha, public_key2) is False
