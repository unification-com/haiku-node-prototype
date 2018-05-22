import json
import os
import shutil
from test.create_lookups import create_lookup_db

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

shutil.copy(
    f"/haiku/haiku_node/keystore/keys-{app_name}.store",
    "/haiku/haiku_node/keystore/keys.store")

# Create lookup database
create_lookup_db(app_name)
shutil.copy(
    f"/haiku/test/data/{app_name}_unification_lookup.db",
    "/haiku/haiku_node/lookup/unification_lookup.db")
