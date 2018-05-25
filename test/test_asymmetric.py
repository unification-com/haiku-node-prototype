import pytest

from haiku_node.config.keys import get_public_key, get_private_key
from haiku_node.validation.encryption import (
    sign_request, verify_request, encrypt, decrypt)


def test_sign_and_verify():
    """
    App2 makes a request to App1
    """
    private_key = get_private_key('app2')
    public_key = get_public_key('app2')

    message = 'request body'
    signature = sign_request(private_key, message)

    broken_signature = 'unlucky' + signature[7:]

    from cryptography.exceptions import InvalidSignature
    with pytest.raises(InvalidSignature):
        verify_request(public_key, message, broken_signature)

    verify_request(public_key, message, signature)


def test_get_public_key():
    from haiku_node.config.keys import get_public_key, get_private_key

    assert get_public_key('app2') is not None
    assert get_private_key('app2') is not None


def test_encryption_over_json():
    import json

    data_body = "this is the original text"

    public_key = get_public_key('app2')
    private_key = get_private_key('app2')

    data = json.dumps({'body': encrypt(public_key, data_body)})
    reload = json.loads(data)
    plain_text_body = decrypt(private_key, reload['body'])

    assert plain_text_body == data_body


def test_generate_keys():
    from haiku_node.validation.encryption import generate_keys
    private_pem, public_pem = generate_keys()
    print(private_pem, public_pem)
