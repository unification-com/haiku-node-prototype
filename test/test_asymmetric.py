# encoding: utf-8

import json
import os
import pytest

from cryptography.exceptions import InvalidSignature
from cryptography.fernet import InvalidToken

from haiku_node.encryption.payload import __bundle, __unbundle
from haiku_node.encryption.tools import (
    symmetric_encrypt, symmetric_decrypt, sign_request, verify_request)
from haiku_node.keystore.keystore import UnificationKeystore

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
    current_path = Path(os.path.dirname(os.path.abspath(__file__)))
    ks_path = current_path / Path('data/keys')
    ks = UnificationKeystore(
        encoded_password, app_name=app_name, keystore_path=ks_path)
    return ks.get_rpc_auth_private_key()


def mock_get_public_key(app_name):
    encoded_password = str.encode(password_for_app(app_name))
    current_path = Path(os.path.dirname(os.path.abspath(__file__)))
    ks_path = current_path / Path('data/keys')
    ks = UnificationKeystore(
        encoded_password, app_name=app_name, keystore_path=ks_path)
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
    private_key = mock_get_private_key('app2')
    public_key = mock_get_public_key('app2')

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

    sender = 'app1'
    recipient = 'app2'

    sender_priv_key = mock_get_private_key(sender)
    recipient_pub_key = mock_get_public_key(recipient)

    sender_pub_key = mock_get_public_key(sender)
    recipient_priv_key = mock_get_private_key(recipient)

    message = __bundle(
        sender_priv_key, recipient_pub_key, sender, payload_d, 'Success')
    wire_data = json.dumps(message)

    with pytest.raises(InvalidToken):
        __unbundle(recipient_priv_key, sender_pub_key,
                   broken(json.loads(wire_data), 'payload'))

    with pytest.raises(InvalidSignature):
        __unbundle(recipient_priv_key, sender_pub_key,
                   broken(json.loads(wire_data), 'signature'))

    reload = json.loads(wire_data)
    reload_d = __unbundle(recipient_priv_key, sender_pub_key, reload)
    assert payload_d == reload_d
