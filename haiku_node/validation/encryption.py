import base64

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa


def padding_encryption():
    """
    Being explicit that the encryption padding is different from the signature
    padding for no good reason.
    """
    return padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )


def padding_signing():
    return padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    )


def sign_request(private_key, message):
    signature = private_key.sign(
        bytes(message, encoding='utf8'), padding_signing(), hashes.SHA256())
    return str(base64.b64encode(signature), encoding='utf-8')


def verify_request(public_key, body, signature):
    public_key.verify(
        base64.b64decode(signature), bytes(body, encoding='utf-8'),
        padding_signing(), hashes.SHA256())


def encrypt(public_key, plaintext):
    """
    JSON transmittable encryption.

    :param public_key:
    :param plaintext: unicode body
    :return: base64encoded encrypted text

    #TODO: Concat the plaintext until we are able to encrypt large documents
    """
    MAGIC_CONCAT_NUMBER = 190

    concatenated = plaintext[:MAGIC_CONCAT_NUMBER]

    encrypted_body = public_key.encrypt(
        concatenated.encode('utf-8'), padding_encryption())
    return base64.encodebytes(encrypted_body).decode('utf-8')


def decrypt(private_key, ciphertext):
    """
    Decryption base64encoded ciphertext from JSON response.

    :param private_key:
    :param ciphertext: base64encoded ciphertext
    :return:
    """
    base64decoded = base64.decodebytes(ciphertext.encode('utf-8'))
    return private_key.decrypt(
        base64decoded, padding_encryption()).decode('utf-8')


def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem, public_pem
