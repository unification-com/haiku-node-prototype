import ecdsa
from binascii import hexlify, unhexlify
from eospy.keys import EOSKey
from eospy.utils import hex_to_int


class UnifEosKey(EOSKey):

    def verify_pub_key(self, encoded_sig, digest, pub_key):
        ''' '''
        # remove SIG_ prefix
        encoded_sig = encoded_sig[4:]
        # remove curve prefix
        curvePre = encoded_sig[:3].strip('_')
        if curvePre != 'K1':
            raise TypeError('Unsupported curve prefix {}'.format(curvePre))

        decoded_sig = self._check_decode(encoded_sig[3:], curvePre)
        # first 2 bytes are recover param
        recover_param = hex_to_int(decoded_sig[:2]) - 4 - 27
        # use sig
        sig = decoded_sig[2:]
        # verify sig
        vk = self._recover_key(unhexlify(digest), unhexlify(sig), recover_param)

        order = ecdsa.SECP256k1.order
        p = vk.pubkey.point
        x_str = ecdsa.util.number_to_string(p.x(), order)
        hex_data = bytearray(chr(2 + (p.y() & 1)), 'utf-8')
        compressed = hexlify(hex_data + x_str).decode()
        p_key = 'EOS' + self._check_encode(compressed).decode()
        return p_key == pub_key
