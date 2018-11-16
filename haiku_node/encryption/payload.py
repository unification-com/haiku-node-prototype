import json

from haiku_node.config.keys import get_public_key
from haiku_node.encryption.tools import (
    symmetric_encrypt, symmetric_decrypt,
    asymmetric_encrypt, asymmetric_decrypt,
    sign_request, verify_request)
from haiku_node.keystore.keystore import UnificationKeystore

dec = lambda s: s.decode('utf-8')
enc = lambda s: s.encode('utf-8')


def bundle(ks: UnificationKeystore, uapp_contract: str, recipient: str,
           message_d: dict, message: str) -> dict:
    """
    Bundle an encrypted payload.

    """
    sender_priv_key = ks.get_rpc_auth_private_key()
    recipient_pub_key = get_public_key(recipient)

    return __bundle(
        sender_priv_key, recipient_pub_key, uapp_contract, message_d, message)


def __bundle(sender_priv_key, recipient_pub_key, sender: str, message_d: dict,
             message: str) -> dict:
    """
    Pure implementation of bundling an encrypted payload.

    """
    payload = json.dumps(message_d)
    token, key = symmetric_encrypt(payload)

    signature = sign_request(sender_priv_key, payload)
    encrypted_key = asymmetric_encrypt(recipient_pub_key, key)

    return {
        'eos_account_name': sender,
        'payload': dec(token),
        'key': dec(encrypted_key),
        'signature': signature,
        'success': True,
        'message': message
    }


def unbundle(ks: UnificationKeystore, sender: str, reload: dict) -> dict:
    """
    Un-bundle a JSON payload.

    """
    recipient_priv_key = ks.get_rpc_auth_private_key()
    public_key = get_public_key(sender)

    return __unbundle(recipient_priv_key, public_key, reload)


def __unbundle(recipient_priv_key, sender_pub_key, reload: dict) -> dict:
    """
    Pure implementation of un-bundle a JSON payload.

    """
    symmetric_key = asymmetric_decrypt(recipient_priv_key, reload['key'])
    decrypted = symmetric_decrypt(
        bytes(reload['payload'], encoding='utf-8'), symmetric_key)

    bundle_d = json.loads(decrypted)
    verify_request(sender_pub_key, decrypted, reload['signature'])

    return bundle_d
