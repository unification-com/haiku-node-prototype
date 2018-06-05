import json

from haiku_node.config.keys import get_private_key, get_public_key
from haiku_node.validation.encryption import (
    symmetric_encrypt, symmetric_decrypt,
    asymmetric_encrypt, asymmetric_decrypt,
    sign_request, verify_request)

dec = lambda s: s.decode('utf-8')
enc = lambda s: s.encode('utf-8')


def bundle(sender: str, recipient: str, message_d: dict, message: str) -> dict:
    """
    Bundle an encrypted payload.

    """
    private_key = get_private_key(sender)
    public_key = get_public_key(recipient)

    payload = json.dumps(message_d)
    token, key = symmetric_encrypt(payload)

    signature = sign_request(private_key, payload)
    encrypted_key = asymmetric_encrypt(public_key, key)

    return {
        'eos_account_name': sender,
        'payload': dec(token),
        'key': dec(encrypted_key),
        'signature': signature,
        'success': True,
        'message': message
    }


def unbundle(sender: str, recipient: str, reload: dict) -> dict:
    """
    Un-bundle a JSON payload.

    """
    private_key = get_private_key(recipient)
    public_key = get_public_key(sender)

    symmetric_key = asymmetric_decrypt(private_key, reload['key'])
    decrypted = symmetric_decrypt(
        bytes(reload['payload'], encoding='utf-8'), symmetric_key)

    bundle_d = json.loads(decrypted)
    verify_request(public_key, decrypted, reload['signature'])

    return bundle_d
