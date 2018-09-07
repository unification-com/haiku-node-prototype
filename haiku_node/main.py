import os

import click
import json

from cryptography.fernet import Fernet

from haiku_node.client import HaikuDataClient, Provider
from haiku_node.config.config import UnificationConfig
from haiku_node.keystore.keystore import UnificationKeystore
from haiku_node.rpc import app
from eosapi import Client
from haiku_node.blockchain_helpers import eosio_account
from haiku_node.blockchain.uapp import UnificationUapp
from haiku_node.blockchain_helpers.eosio_cleos import EosioCleos

PORT = 8050

bold = lambda s: click.style(str(s), bold=True)


@click.group()
def main():
    pass


def spawn_haiku_node(pw, config):
    encoded_password = str.encode(pw)
    ks = UnificationKeystore(encoded_password)

    setattr(app, 'keystore', ks)
    setattr(app, 'unification_config', config)
    app.run(debug=False, host="0.0.0.0", port=PORT, ssl_context='adhoc')


@main.command()
@click.argument('password', required=False)
def serve(password):
    """
    Serve the Haiku RPC service.
    """
    config = UnificationConfig()

    if not config['server_initialised']:
        click.echo(f'Server not initialized: Run {bold("haiku init")}')
    else:
        if password:
            spawn_haiku_node(password, config)
        else:
            env_password = os.environ.get('keystore')
            if not env_password:
                click.echo('Password to keystore not provided in args nor set '
                           'as the keystore ENV VAR')
            else:
                spawn_haiku_node(env_password, config)


@main.command()
def init():
    """
    Initialize the Haiku Server.
    """
    config = UnificationConfig()

    if config['server_initialised']:
        click.echo(f'Server already initialized')
    else:
        pw = Fernet.generate_key()
        click.echo("Generated password:\n")
        click.echo(bold(pw.decode('utf-8')))
        click.echo("\n")
        click.echo("IMPORTANT: KEEP THIS SAFE!! YOU WILL NEED IT TO RUN THE "
                   "SERVER")
        click.echo("Run again with pw")

        config["server_initialised"] = True


@main.command()
@click.argument('provider')
@click.argument('request_hash')
@click.option('--user', default=None)
def fetch(provider, request_hash, user):
    """
    Fetch data from an App to this App for a particular user.

    \b
    :param provider: The app name of the data provider.
    :param request_hash: The particular piece of data in concern.
    :param user: Obtain data for a specific user EOS user account.
    :return:
    """
    requesting_app = os.environ['app_name']
    password = os.environ['keystore']

    # TODO: get host and port values from MOTHER, by passing provider name
    provider = Provider(provider, 'https', f'haiku-{provider}', PORT)
    req_hash = f'request-{request_hash}'

    suffix = 'for all users' if user is None else f'for {user}'
    click.echo(f'App {requesting_app} is requesting data from {provider.name}'
               f' {suffix}')

    encoded_password = str.encode(password)
    keystore = UnificationKeystore(encoded_password)

    client = HaikuDataClient(keystore)
    data_path = client.make_data_request(
        requesting_app, provider, user, req_hash)
    click.echo(f'Data written to {data_path}')


@main.command()
@click.argument('provider')
@click.argument('request_hash')
def view(provider, request_hash):
    """
    Read data stored locally from an Data Provider for a particular user.

    \b
    :param provider: The app name of the data provider.
    :param request_hash: The particular piece of data in concern.
    :return:
    """
    requesting_app = os.environ['app_name']
    password = os.environ['keystore']

    provider = Provider(provider, 'https', f'haiku-{provider}', PORT)
    req_hash = f'request-{request_hash}'

    click.echo(f'App {requesting_app} is reading ingested data from '
               f'{provider.name}')

    encoded_password = str.encode(password)
    keystore = UnificationKeystore(encoded_password)

    client = HaikuDataClient(keystore)
    data = client.read_data_from_store(provider, req_hash)

    json_obj = json.loads(data)

    print(json_obj)


@main.command()
def uapp_store():
    """
    Display a list of valid apps, and their schemas.
    Allow option to initiate a data transfer
    \b

    :param consumer: The app name of the data consumer.
    :param password: The data consumer's wallet password.
    """

    requesting_app = os.environ['app_name']

    click.echo(bold("UApp Store"))

    conf = UnificationConfig()
    eos_client = Client(
        nodes=[f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}"])

    valid_apps = eos_client.get_table_rows(
        "unif.mother", "unif.mother", "validapps", True, 0, -1,
        -1)

    uapp_store = {}
    store_key = 1

    for va in valid_apps['rows']:
        data_provider = eosio_account.name_to_string(int(va['acl_contract_acc']))
        if int(va['is_valid']) == 1 and data_provider != requesting_app:
            uapp_sc = UnificationUapp(eos_client, data_provider)
            db_schemas = uapp_sc.get_all_db_schemas()
            click.echo(bold(f"Data Provider: {data_provider}"))
            for schema_pkey, db_schema in db_schemas.items():
                schema = db_schema['schema']
                click.echo(bold(f"Option {store_key}:"))
                click.echo("    Data available:")
                for field in schema['fields']:
                    click.echo(f"        {field['name']}, {field['type']}")
                click.echo(f"    Scheduled Price: {db_schema['price_sched']} UND")
                click.echo(f"    Ad-hoc Price: {db_schema['price_adhoc']} UND")
                click.echo("    Availability: daily")

                d = {
                    'provider': data_provider,
                    'schema_pkey': schema_pkey,
                    'price': db_schema['price_sched']
                }
                uapp_store[store_key] = d
                store_key += 1

    request_id = int(input(f"Select option 1 - {(store_key - 1)} to initialise a data request, or '0' to exit:"))
    if request_id > 0 and request_id <= store_key:
        data_request = uapp_store[request_id]
        __request_from_uapp_store(data_request)
    else:
        click.echo("Exit Uapp Store")


def __request_from_uapp_store(data_request):
    requesting_app = os.environ['app_name']
    password = os.environ['keystore']

    click.echo("Processing request:")
    click.echo(data_request)

    conf = UnificationConfig()
    eos_client = Client(
        nodes=[f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}"])

    uapp_sc = UnificationUapp(eos_client, requesting_app)

    latest_req_id = uapp_sc.init_data_request(data_request['provider'], data_request['schema_pkey'], "0",
                                              data_request['price'])

    request_hash = f"{data_request['provider']}-{data_request['schema_pkey']}-{latest_req_id}.dat"

    provider = Provider(data_request['provider'], 'https', f"haiku-{data_request['provider']}", PORT)
    req_hash = f'request-{request_hash}'

    click.echo(f'App {requesting_app} is requesting data from {provider.name}')

    encoded_password = str.encode(password)
    keystore = UnificationKeystore(encoded_password)

    client = HaikuDataClient(keystore)
    data_path = client.make_data_request_uapp_store(
        requesting_app, provider, latest_req_id, req_hash)
    click.echo(f'Data written to {data_path}')


if __name__ == "__main__":
    main()
