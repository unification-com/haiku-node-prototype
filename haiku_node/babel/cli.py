import logging
import os

import click

from haiku_node.client import HaikuDataClient, Provider
from haiku_node.keystore.keystore import UnificationKeystore

log = logging.getLogger(__name__)


@click.group()
def main():
    pass


@main.command()
@click.argument('app_name')
@click.argument('request_hash')
def fetch(app_name, request_hash):
    requesting_app = os.environ['app_name']
    password = os.environ['keystore']

    provider = Provider(app_name, 'https', f'haiku-{app_name}', 8050)
    req_hash = f'request-{request_hash}'

    click.echo(f'App {requesting_app} is requesting data from {provider.name}')

    encoded_password = str.encode(password)
    keystore = UnificationKeystore(encoded_password)

    client = HaikuDataClient(keystore)
    data_path = client.make_data_request(requesting_app, provider, req_hash)
    click.echo(f'Data written to {data_path}')


@main.command()
@click.argument('app_name')
@click.argument('request_hash')
def read(app_name, request_hash):
    requesting_app = os.environ['app_name']
    password = os.environ['keystore']

    provider = Provider(app_name, 'https', f'haiku-{app_name}', 8050)
    req_hash = f'request-{request_hash}'

    click.echo(f'App {requesting_app} is reading ingested data from '
               f'{provider.name}')

    encoded_password = str.encode(password)
    keystore = UnificationKeystore(encoded_password)

    client = HaikuDataClient(keystore)
    data = client.read_data_from_store(provider, req_hash)
    click.echo(data)


if __name__ == "__main__":
    main()
