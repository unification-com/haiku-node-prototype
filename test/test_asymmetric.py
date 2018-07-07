# encoding: utf-8

import json
import os
import pytest

from cryptography.exceptions import InvalidSignature
from cryptography.fernet import InvalidToken

from haiku_node.encryption.payload import bundle, unbundle
from haiku_node.encryption.tools import (
    symmetric_encrypt, symmetric_decrypt, sign_request, verify_request)
from haiku_node.keystore.keystore import UnificationKeystore

from unittest.mock import patch
from pathlib import Path


def password_for_app(app_name):
    """
    The key stores currently do not contain the public keys of the peer apps
    """
    current_directory = Path(os.path.abspath(__file__))
    par = current_directory.parent.parent
    config = par / Path('test/data/demo_config.json')

    contents = config.read_text()
    d = json.loads(contents)["system"]

    return d[app_name]['password']


def mock_get_private_key(app_name):
    encoded_password = str.encode(password_for_app(app_name))
    ks = UnificationKeystore(encoded_password, app_name=app_name)
    return ks.get_rpc_auth_private_key()


def mock_get_public_key(app_name):
    encoded_password = str.encode(password_for_app(app_name))

    ks = UnificationKeystore(encoded_password, app_name=app_name)
    return ks.get_rpc_auth_public_key()


def test_get_public_key():
    get_public_key = mock_get_public_key
    get_private_key = mock_get_private_key

    assert get_public_key('app2') is not None
    assert get_private_key('app2') is not None


def test_generate_keys():
    from haiku_node.encryption.tools import generate_keys
    private_pem, public_pem = generate_keys()
    print(private_pem, public_pem)


def test_symmetric():
    data_body = "this is the original text"
    token, key = symmetric_encrypt(data_body)

    decrypted_body = symmetric_decrypt(token, key)
    assert decrypted_body == data_body


@pytest.mark.parametrize("message", [
    "bar",
    "x" * 100000,
    "'¡ooʇ ןnɟǝsn sı uʍop-ǝpısdn unicode ¡ooʇ ןnɟǝsn sı uʍop-ǝpısdn"
])
def test_sign_and_verify(message):
    get_public_key = mock_get_public_key
    get_private_key = mock_get_private_key

    private_key = get_private_key('app2')
    public_key = get_public_key('app2')

    signature = sign_request(private_key, message)

    broken_signature = 'unlucky' + signature[7:]

    with pytest.raises(InvalidSignature):
        verify_request(public_key, message, broken_signature)

    verify_request(public_key, message, signature)


@pytest.mark.parametrize("payload_d", [
    {},
    {'foo': 'bar'},
    {'foo': '¡ooʇ ןnɟǝsn sı uʍop-ǝpısdn unicode ¡ooʇ ןnɟǝsn sı uʍop-ǝpısdn'},
    {'big_field': "x" * 100000},
])
def test_transfer_over_json(payload_d):
    """
    App1 returns a data payload back to App2
    """

    def broken(d, field):
        d[field] = 'unlucky' + d[field][7:]
        return d

    with patch('haiku_node.encryption.payload.get_public_key',
               mock_get_public_key):
        sender = 'app1'
        recipient = 'app2'

        message = bundle(sender, recipient, payload_d, 'Success')
        wire_data = json.dumps(message)

        with pytest.raises(InvalidToken):
            unbundle(
                sender, recipient, broken(json.loads(wire_data), 'payload'))

        with pytest.raises(InvalidSignature):
            unbundle(
                sender, recipient, broken(json.loads(wire_data), 'signature'))

        reload = json.loads(wire_data)
        reload_d = unbundle(sender, recipient, reload)
        assert payload_d == reload_d
