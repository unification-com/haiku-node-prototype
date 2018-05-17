import json
import os
import shutil

from pathlib import Path

config = Path('data/system.json')

contents = config.read_text()
d = json.loads(contents)

app_name = os.environ['app_name']
password = d[app_name]['password']

print(f"Setting up host for {app_name}")

with open('/etc/haiku-password', 'w') as f:
    f.write(password)

os.unlink('/haiku/haiku_node/keystore/keys.store')

shutil.move(
    f"/haiku/haiku_node/keystore/keys-{app_name}.store",
    "/haiku/haiku_node/keystore/keys.store")
