import json
import os
import shutil

from pathlib import Path

from create_lookups import create_lookup_db
from haiku_node.config.config import UnificationConfig

demo_config = json.loads(Path('data/demo_config.json').read_text())
password_d = demo_config["system"]

app_name = os.environ['app_name']
password = password_d[app_name]['password']

print(f"Setting up host for {app_name}")

os.unlink('/haiku/haiku_node/keystore/keys.store')

shutil.copy(
    f"/haiku/haiku_node/keystore/keys-{app_name}.store",
    "/haiku/haiku_node/keystore/keys.store")

# Create lookup database
print(f"Create lookup db for {app_name}")
create_lookup_db(app_name)
shutil.copy(
    f"/haiku/test/data/{app_name}_unification_lookup.db",
    "/haiku/haiku_node/lookup/unification_lookup.db")

os.unlink(f"/haiku/test/data/{app_name}_unification_lookup.db")

print(f"set config/config.json values for host {app_name}")
uc = UnificationConfig()
uc.set_conf("acl_contract", app_name)

print("config.json:")
print(uc.get_conf())
