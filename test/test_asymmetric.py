import pytest

from haiku_node.config.keys import get_public_key, get_private_key
from haiku_node.validation.encryption import sign_request, verify_request


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
