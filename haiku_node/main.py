import os

import click
import json

from cryptography.fernet import Fernet

from haiku_node.blockchain.eos.mother import UnificationMother
from haiku_node.blockchain.eos.uapp import UnificationUapp
from haiku_node.blockchain_helpers.eos import eosio_account
from haiku_node.config.config import UnificationConfig
from haiku_node.client import HaikuDataClient, Provider
from haiku_node.keystore.keystore import UnificationKeystore
from haiku_node.network.eos import get_eos_rpc_client
from haiku_node.rpc import app

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
    Fetch data from an App to this App in an Enterprise/DSP/B2B environment,
    where data request is agreed external to the UApp Store.

    \b
    :param provider: The app name of the data provider.
    :param request_hash: The particular piece of data in concern.
    :param user: Obtain data for a specific user EOS user account.
    :return:
    """
    requesting_app = os.environ['app_name']
    password = os.environ['keystore']

    # Write the data request to the Consumer's UApp smart contract
    eos_client = get_eos_rpc_client()
    mother = UnificationMother(eos_client, provider)

    provider = Provider(provider, 'https', mother)
    req_hash = f'request-{request_hash}'

    suffix = 'for all users' if user is None else f'for {user}'
    click.echo(f'App {requesting_app} is requesting data from {provider}'
               f' {suffix}')

    encoded_password = str.encode(password)
    keystore = UnificationKeystore(encoded_password)

    # tmp - get the price for the transfer from Schema[0] in provider's UApp SC
    # This will possibly be determined externally as part of the B2B agreement
    provider_uapp_sc = UnificationUapp(eos_client, provider)
    db_schema = provider_uapp_sc.get_db_schema_by_pkey(0)  # tmp - only 1 schema
    sched_price = db_schema['price_sched']

    # initiate request in Consumer's UApp SC
    consumer_uapp_sc = UnificationUapp(eos_client, requesting_app)
    latest_req_id = consumer_uapp_sc.init_data_request(
        provider, "0", "0", sched_price)

    client = HaikuDataClient(keystore)
    data_path = client.make_data_request(
        requesting_app, provider, user, req_hash, latest_req_id)

    click.echo(f'Data written to: {data_path}')
    click.echo(f'View using: haiku view {provider.name} {request_hash}')


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

    eos_client = get_eos_rpc_client()
    mother = UnificationMother(eos_client, provider)

    provider_obj = Provider(provider, 'https', mother)
    req_hash = f'request-{request_hash}'

    click.echo(f'App {requesting_app} is reading ingested data from '
               f'{provider_obj.name}')

    encoded_password = str.encode(password)
    keystore = UnificationKeystore(encoded_password)

    client = HaikuDataClient(keystore)
    data = client.read_data_from_store(provider_obj, req_hash)

    click.echo(json.loads(data))


@main.command()
def uapp_store():
    """
    Display a list of valid apps, and their schemas.
    Allow option to initiate and process a data transfer
    \b
    """
    requesting_app = os.environ['app_name']

    click.echo(bold("UApp Store"))

    eos_client = get_eos_rpc_client()
    valid_apps = eos_client.get_table_rows(
        "unif.mother", "unif.mother", "validapps", True, 0, -1,
        -1)

    uapp_store_dict = {}
    store_key = 1

    for va in valid_apps['rows']:
        data_provider = eosio_account.name_to_string(
            int(va['acl_contract_acc']))
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
                uapp_store_dict[store_key] = d
                store_key += 1

    request_id = int(input(f"Select option 1 - {(store_key - 1)} to generate "
                           f"a data request, or '0' to exit:"))
    if 0 < request_id <= store_key:
        data_request = uapp_store_dict[request_id]
        __request_from_uapp_store(data_request)
    else:
        click.echo("Exit Uapp Store")


def __request_from_uapp_store(data_request):
    """
    Receives a data request from the UApp Store, and
    processes the request

    \b
    :param data_request: Dict containing request parameters
    """
    requesting_app = os.environ['app_name']
    password = os.environ['keystore']

    click.echo("Processing request from UApp Store:")
    click.echo(data_request)

    eos_client = get_eos_rpc_client()

    # Write the data request to the Consumer's smart contract
    uapp_sc = UnificationUapp(eos_client, requesting_app)
    latest_req_id = uapp_sc.init_data_request(
        data_request['provider'], data_request['schema_pkey'], "0",
        data_request['price'])

    request_hash = f"{data_request['provider']}-{data_request['schema_pkey']}" \
                   f"-{latest_req_id}.dat"

    provider_name = data_request['provider']
    mother = UnificationMother(eos_client, provider_name)
    provider_obj = Provider(provider_name, 'https', mother)
    req_hash = f'request-{request_hash}'

    click.echo(f'App {requesting_app} is requesting data from '
               f'{provider_obj.name}')

    encoded_password = str.encode(password)
    keystore = UnificationKeystore(encoded_password)

    client = HaikuDataClient(keystore)
    data_path = client.make_data_request(
        requesting_app, provider_obj, None, req_hash, latest_req_id)

    click.echo(f'Data written to: {data_path}')
    click.echo(f'View using: haiku view {provider_obj.name} {request_hash}')


if __name__ == "__main__":
    main()
