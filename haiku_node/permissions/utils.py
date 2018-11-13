from haiku_node.blockchain_helpers.eos.eos_keys import UnifEosKey
from haiku_node.encryption.jwt.jwt import UnifJWT
from haiku_node.utils.utils import generate_nonce, generate_perm_digest_sha


def generate_payload(user, private_key, provider, consumer, granted_fields_str,
                     perm, schema_id):
    p_nonce = generate_nonce(16)
    perm_digest_sha = generate_perm_digest_sha(
        granted_fields_str, schema_id, p_nonce, consumer)

    # sign permission changes
    eosk = UnifEosKey(private_key)
    p_sig = eosk.sign(perm_digest_sha)

    jwt_payload = {
        'iss': user,  # RFC 7519 4.1.1
        'sub': 'perm_request',  # RFC 7519 4.1.2
        'aud': provider,  # RFC 7519 4.1.3
        'eos_perm': perm,
        'consumer': consumer,
        'schema_id': schema_id,
        'perms': granted_fields_str,
        'p_nonce': p_nonce,
        'p_sig': p_sig
    }

    unif_jwt = UnifJWT()
    unif_jwt.generate(jwt_payload)
    unif_jwt.sign(private_key)
    jwt = unif_jwt.to_jwt()

    payload = {
        'jwt': jwt,
        'eos_perm': perm,
        'user': user,
        'provider': provider
    }

    return payload, p_nonce, p_sig
