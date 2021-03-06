import json
import os
import shutil

from pathlib import Path

from haiku_node.config.config import UnificationConfig

demo_config = json.loads(Path('data/demo_config.json').read_text())
password_d = demo_config["system"]

app_name = os.environ['app_name']
password = password_d[app_name]['password']

print(f"Setting up host for {app_name}")

shutil.copy(
    f"/haiku/test/data/keys/keys-{app_name}.store",
    "/haiku/haiku_node/keystore/keys.store")

shutil.copy(
    f"/haiku/test/data/lookups/{app_name}.unification_lookup.db",
    "/haiku/haiku_node/dbs/unification_lookup.db")

shutil.copy(
    f"/haiku/test/data/sqlite/{app_name}.db",
    "/haiku/haiku_node/dbs/Data.db")

shutil.copy(
    f"/haiku/test/data/perm_batch/{app_name}.perm_batches.db",
    "/haiku/haiku_node/dbs/perm_batches.db")

shutil.copy(
    f"/haiku/test/data/adhoc/{app_name}.adhoc.db",
    "/haiku/haiku_node/dbs/adhoc.db")

print(f"set config/config.json values for host {app_name}")
uc = UnificationConfig()
uc["uapp_contract"] = app_name
uc["eos_rpc_ip"] = "nodeosd"

# set up DB config values
dbs = {}

for schemas in demo_config['demo_apps'][app_name]['db_schemas']:
    db = {
        'filename': schemas['filename'],
    }
    dbs[schemas['sc_schema_pkey']] = db

uc['db_conn'] = dbs

print("config.json:")
print(uc)
