# encoding: utf-8

import json

import pytest

from cryptography.exceptions import InvalidSignature
from cryptography.fernet import InvalidToken

from haiku_node.config.keys import get_public_key, get_private_key
from haiku_node.validation.encryption import (
    symmetric_encrypt, symmetric_decrypt)
from haiku_node.validation.payload import bundle, unbundle


def test_get_public_key():
    assert get_public_key('app2') is not None
    assert get_private_key('app2') is not None


def test_generate_keys():
    from haiku_node.validation.encryption import generate_keys
    private_pem, public_pem = generate_keys()
    print(private_pem, public_pem)


def test_symmetric():
    data_body = "this is the original text"
    token, key = symmetric_encrypt(data_body)

    decrypted_body = symmetric_decrypt(token, key)
    assert decrypted_body == data_body


@pytest.mark.parametrize("payload_d", [
    {},
    {'foo': 'bar'},
    {'foo': '¡ooʇ ןnɟǝsn sı uʍop-ǝpısdn unicode ¡ooʇ ןnɟǝsn sı uʍop-ǝpısdn'},
    {'big_field': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890'},  # noqa
])
def test_transfer_over_json(payload_d):
    """
    App1 returns a data payload back to App2
    """

    def broken(d, field):
        d[field] = 'unlucky' + d[field][7:]
        return d

    sender = 'app1'
    recipient = 'app2'

    message = bundle(sender, recipient, payload_d, 'Success')
    wire_data = json.dumps(message)

    with pytest.raises(InvalidToken):
        unbundle(sender, recipient, broken(json.loads(wire_data), 'payload'))

    with pytest.raises(InvalidSignature):
        unbundle(sender, recipient, broken(json.loads(wire_data), 'signature'))

    reload = json.loads(wire_data)
    reload_d = unbundle(sender, recipient, reload)
    assert payload_d == reload_d
