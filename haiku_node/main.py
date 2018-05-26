import os
import sys

from cryptography.fernet import Fernet

from haiku_node.config.config import UnificationConfig
from haiku_node.keystore.keystore import UnificationKeystore
from haiku_node.rpc import app

PORT = 8050


def spawn_haiku_node(pw, config):
    encoded_password = str.encode(pw)
    ks = UnificationKeystore(encoded_password)

    setattr(app, 'keystore', ks)
    setattr(app, 'unification_config', config)
    app.run(debug=False, host="0.0.0.0", port=PORT, ssl_context='adhoc')


if __name__ == '__main__':
    conf = UnificationConfig()

    password = os.environ.get('keystore')
    if password:
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

            conf["server_initialised"] = True
