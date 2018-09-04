import os

import click
import json, xmljson
from lxml.etree import fromstring

from cryptography.fernet import Fernet

from haiku_node.client import HaikuDataClient, Provider
from haiku_node.config.config import UnificationConfig
from haiku_node.keystore.keystore import UnificationKeystore
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

    # if 'no-data' not in json_obj:
    #     users_to_pay = json_obj['data']['unification_users']
    #     if isinstance(users_to_pay, dict):
    #         username = users_to_pay['unification_user']
    #         print(f'pay {username}')
    #         ret = und_reward.send_reward(username)
    #         log.debug(ret)
    #     else:
    #         for username in users_to_pay['unification_user']:
    #             print(f'pay {username}')
    #             ret = und_reward.send_reward(username)
    #             log.debug(ret)
    #
    #     log.debug(f"Pay provider {providing_app.name}")
    #     ret = und_reward.send_reward(providing_app.name, False)
    #     log.debug(ret)
    #
    #
    #
    #
    # xml_obj = fromstring(data)
    # json_obj = json.loads(json.dumps(xmljson.gdata.data(xml_obj)))
    #
    # data_from = json_obj['data']['from']['$t']
    # timestamp = json_obj['data']['timestamp']['$t']
    # user = json_obj['data']['unification_users']['unification_user']['$t']  # temp hack
    # click.echo(f'data from:' f'{data_from}')
    # click.echo(f'timestamp:' f'{timestamp}')
    # click.echo(f'user:' f'{user}')
    #
    # column = []
    # for items in json_obj['data']['rows']['row']:
    #     for row in range(0, len(items['field'])):
    #         if len(column) < len(items['field']):
    #             column.append(items['field'][row]['field_name']['$t'])
    #
    # print(*column)
    # rows = []
    # for items in json_obj['data']['rows']['row']:
    #     cells = []
    #     for i in range(0, len(items['field'])):
    #         cells.append(items['field'][i]['value']['$t'])
    #     rows.append(cells)
    #
    # for s in rows:
    #     print(*s)


if __name__ == "__main__":
    main()
