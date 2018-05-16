import sys

from cryptography.fernet import Fernet
from pathlib import Path

from haiku_node.config.config import UnificationConfig
from haiku_node.keystore.keystore import UnificationKeystore
from haiku_node.rpc import app

# A plain text on the file-system password to ease automated systems
HAIKU_PASSWORD_FILE = Path('/etc/haiku-password')


def spawn_haiku_node(pw, conf):
    print(pw)
    print(conf)
    ks = UnificationKeystore(pw)
    ks.set_encryption_key(
        "user1", "app2",
        "EOS4yMT6jNNsrsSxX26xeVCjQkqsUUiMzCEaHCTvLo5tR1JmBuE3C")
    ks.set_encryption_key(
        "user1", "app3",
        "EOS74UxTtX4mY1d716PkMSi3B9r97yseB9ogHvohdjmT8r8emnFTz")

    print("user1, app2: ", ks.get_encryption_key("user1", "app2"))
    print("user1, app3: ", ks.get_encryption_key("user1", "app3"))

    priv = '-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEApakS8qunhjD+/rLhs90sX4QIh7qWV/6kirBF6plZZHBUHQUz\n90nZQH0zl0feneHXxOEvm1ogLkLtj8qqByzUl7mvzsEdGvtn2AuZt6WzkCThKyhQ\noVU3GVG48xUz8YviR/CruUSlPFeg0DT67IEW3iKYsLWxr9R4D+W5ffRk92/s41Tu\n6b1n4KobTyzvvFSzKlJo6I9a7M4ZvyikWQQri0MUyezMzjDgYNXueGG8gX2VP7OQ\nbvPMb40okN4J3G2gmj9SXf89o8pPDAnk3c1fl1RJ25MjZcVCLFMnI6PBIleCjmtV\n5YqgFznCyLXFcfqieiMb0sPRqhrmB77WjWzVnwIDAQABAoIBAGOdnOBCKnW+Jsgf\n5ysSV6mEKuD7aYa2gFlJkHF3D1MfXOUqiMouJS7rWseglxRXhzlDtC317x4Cbvol\ng0LXSWuHZFmutILSJOq8Zw4Q3T5TfvdFwd6R8JUQGGhMGrUoScS6y3iX98imZPRu\nt2jaY1bmdOzmBVhXKm9c08MS4FgNhKWfruwj8eY5kMOaF/apdsEPN5HmOLDB7xFh\nuRYOg1ZDAVDZeoQTNpOR6eOYuYuONWFMRVA+F4SqWWbmaJjwG55eV+7WDIwJg/5w\nijTCy9A4MMihG3rraQQ5vFJlpVcGV6UnwjOLnEYsMFqedRNaIv5vm/YfLebiWtog\noZw9xvkCgYEA3HF4IKyjAwyWxNeVuQqfevKnry7usrGCyIptyskfRAq6Z88hUV1f\nzCj3ST7Zlh46IrQxaukV7jNmVaKYyAZXptJciqbw3A9GcwvZvKDfZUQmd6jQCtFE\nOeyHkoez+nD+SOfskjWddM3uU3U3PtN0nvMnLQ2b93fvsP189rsgarsCgYEAwGGE\nORDxveTHuYKfLI43s5yVBLHGeRCASwUOqG2Nckbx39MbEzWJQv9HsgS8KzgMHXhn\n7muyv9XaljK+8W7s1UOJfAXTlw+bYZCYw6Org4UWaoK6cVJMOGgAHc2mis1PLZWI\nE8sr+tjioBYRyqp0iY/DRATDbKJnlSAc90KB7G0CgYB8qB3KPFWiL8hCX7bnAL7W\ng8mXIu8QVZkjVkRn2/u2OmrWsSaiIC9AABp2bPgWD9nILiWT02L3ZFGGM4A5/Hws\ndeCm92hUyL6J6DWkmUQ6u6MVH30l4Ni3+K1hiyOXh7YD/EKnG3KCzsDqqOoouOLF\nz7Jjo8KC2mvMpku4KnFWaQKBgQCxhAoXAjyepZFp607nNR/O24hh+YyTP5eyIauB\n3Pzs2uvrRYexNPBAYwCMEnRzSNddBjKYvMYG39VATPkGHP3qV9RwHYw90sfkwiFE\nPS1RQagKhjB1yqPMVKLu3Ul0wLfz7wvOf+ZIJIMRhuvJ33mDSaW7iM2u2zjLUQOJ\nYNQ0DQKBgQDBm7ZvOtdcYmFbTOWQQZp/BpPHvH0/k0FDnsmcbYr3K6wrisF3uCyz\n6hZwSGg4j+ME9UJPc5DBXr97elPhSCipqx10ZcX2Hb5AUS3tizzG+ojeZdDKOCSa\nCTpjvpXSgbCt5ZUcHsMWDpQIPpxhORxwg//D+5ysQBYweGX1/qsojw==\n-----END RSA PRIVATE KEY-----\n' # noqa
    pub = '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApakS8qunhjD+/rLhs90s\nX4QIh7qWV/6kirBF6plZZHBUHQUz90nZQH0zl0feneHXxOEvm1ogLkLtj8qqByzU\nl7mvzsEdGvtn2AuZt6WzkCThKyhQoVU3GVG48xUz8YviR/CruUSlPFeg0DT67IEW\n3iKYsLWxr9R4D+W5ffRk92/s41Tu6b1n4KobTyzvvFSzKlJo6I9a7M4ZvyikWQQr\ni0MUyezMzjDgYNXueGG8gX2VP7OQbvPMb40okN4J3G2gmj9SXf89o8pPDAnk3c1f\nl1RJ25MjZcVCLFMnI6PBIleCjmtV5YqgFznCyLXFcfqieiMb0sPRqhrmB77WjWzV\nnwIDAQAB\n-----END PUBLIC KEY-----\n' # noqa

    ks.set_rpc_auth_keys(pub, priv)

    print("Private auth key: ", ks.get_rpc_auth_private_key())
    print("Public auth key: ", ks.get_rpc_auth_public_key())

    app.run(debug=False, host="0.0.0.0", port=8050)


if __name__ == '__main__':
    config = UnificationConfig()
    conf = config.get_conf()

    if HAIKU_PASSWORD_FILE.exists():
        password = HAIKU_PASSWORD_FILE.read_text()
        spawn_haiku_node(password, conf)

    else:
        if 'server_initialised' in conf:
            if len(sys.argv) > 1:
                pw = sys.argv[1]
                spawn_haiku_node(pw, conf)
            else:
                print("password required")
        else:
            pw = Fernet.generate_key()
            print("Generated password:\n")
            sys.stdout.buffer.write(pw)
            print("\n")
            print("IMPORTANT: KEEP THIS SAFE!! "
                  "YOU WILL NEED IT TO RUN THE SERVER")
            print("Run again with pw")

            config.set_conf("server_initialised", True)
