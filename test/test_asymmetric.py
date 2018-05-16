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

    assert verify_request(public_key, message, broken_signature) is False
    assert verify_request(public_key, message, signature) is True
