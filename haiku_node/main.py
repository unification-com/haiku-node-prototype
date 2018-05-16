import os,sys,inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
sys.path.append("..")

from config.config import UnificationConfig
from cryptography.fernet import Fernet
from keystore.keystore import UnificationKeystore

def spawn_haiku_node(pw, conf):
    print(pw)
    print(conf)
    ks = UnificationKeystore(pw)
    ks.set_key("user1", "app2", "EOS4yMT6jNNsrsSxX26xeVCjQkqsUUiMzCEaHCTvLo5tR1JmBuE3C")
    ks.set_key("user1", "app3", "EOS74UxTtX4mY1d716PkMSi3B9r97yseB9ogHvohdjmT8r8emnFTz")

    print("user1, app2: ", ks.get_key("user1", "app2"))
    print("user1, app3: ", ks.get_key("user1", "app3"))


if __name__ == '__main__':
    config = UnificationConfig()
    conf = config.get_conf()
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
        print("IMPORTANT: KEEP THIS SAFE!! YOU WILL NEED IT TO RUN THE SERVER")
        print("Run again with pw")

        config.set_conf("server_initialised", True)
