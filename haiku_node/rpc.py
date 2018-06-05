import flask

from cryptography.exceptions import InvalidSignature
from eosapi import Client

from haiku_node.config.keys import get_public_key
from haiku_node.data.factory import UnificationDataFactory
from haiku_node.encryption.encryption import verify_request
from haiku_node.encryption.payload import unbundle, bundle
from haiku_node.validation.validation import UnificationAppScValidation

app = flask.Flask(__name__)
app.logger_name = "haiku-rpc"

logger = app.logger


def verify_account(eos_account_name: str, body, signature):
    verify_request(get_public_key(eos_account_name), body, signature)


def invalid_response():
    return flask.jsonify({
        'success': False,
        'message': 'Unauthorized',
        'signature': None,
        'body': None
    }), 401


def unauthorized_for_user():
    return flask.jsonify({
        'success': False,
        'message': 'Unauthorized For User',
        'signature': None,
        'body': None
    }), 401


def generic_error():
    return flask.jsonify({
        'success': False,
        'message': 'Internal Server Error',
        'signature': None,
        'body': None
    }), 500


def invalid_app():
    return flask.jsonify({
        'success': False,
        'message': 'Invalid App',
        'signature': None,
        'body': None
    }), 401


def obtain_data(eos_account_name, eos_client, acl_contract_acc, users):
    """
    :param eos_account_name: The account name of the requesting App.
    :param users: The users to obtain data for.
    """

    data_factory = UnificationDataFactory(
        eos_client, acl_contract_acc, eos_account_name, users)
    body = {
        'data': data_factory.get_raw_data()
    }
    d = bundle(acl_contract_acc, eos_account_name, body, 'Success')
    return flask.jsonify(d), 200


def ingest_data(eos_account_name, eos_client, acl_contract_acc, users):
    response_body = {}

    d = bundle(acl_contract_acc, eos_account_name, response_body, 'Success')
    return flask.jsonify(d), 200


@app.route('/data_request', methods=['POST'])
def data_request():
    try:
        d = flask.request.get_json()

        # Validate requesting app against smart contracts
        # config is this Haiku Node's config fle, containing its ACL/Meta Data
        # Smart Contract account/address and the EOS RPC server/port used for
        # communicating with the blockchain.
        conf = app.unification_config

        sender = d['eos_account_name']
        recipient = conf['acl_contract']
        bundle_d = unbundle(sender, recipient, d)

        eos_client = Client(
            nodes=[f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}"])

        # Init the validation class for THIS Haiku, and validate the
        # REQUESTING APP. Since we only need to validate the app at this point,
        # set get_perms=False
        v = UnificationAppScValidation(
            eos_client, conf['acl_contract'], d['eos_account_name'],
            get_perms=True)

        # If the REQUESTING APP is valid according to MOTHER, then we can
        # generate the data. If not, return an invalid_app response
        # Whatever obtain_data eventually uses to grab the data will also need
        # to load the UnificationAppScValidation class, so it knows which users
        # have granted permissions to the REQUESTING APP, and get the correct
        # data
        if v.valid():
            users = bundle_d.get('users')
            return obtain_data(sender, eos_client, conf['acl_contract'], users)
        else:
            return invalid_app()

    except InvalidSignature:
        return invalid_response()

    except Exception as e:
        logger.exception(e)
        return generic_error()


@app.route('/data_ingest', methods=['POST'])
def data_ingest():
    try:
        d = flask.request.get_json()

        # Validate requesting app against smart contracts
        # config is this Haiku Node's config fle, containing its ACL/Meta Data
        # Smart Contract account/address and the EOS RPC server/port used for
        # communicating with the blockchain.
        conf = app.unification_config

        sender = d['eos_account_name']
        recipient = conf['acl_contract']
        bundle_d = unbundle(sender, recipient, d)

        eos_client = Client(
            nodes=[f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}"])

        # Init the validation class for THIS Haiku, and validate the
        # REQUESTING APP. Since we only need to validate the app at this point,
        # set get_perms=False
        v = UnificationAppScValidation(
            eos_client, conf['acl_contract'], d['eos_account_name'],
            get_perms=True)

        # If the REQUESTING APP is valid according to MOTHER, then we can
        # generate the data. If not, return an invalid_app response
        # Whatever obtain_data eventually uses to grab the data will also need
        # to load the UnificationAppScValidation class, so it knows which users
        # have granted permissions to the REQUESTING APP, and get the correct
        # data
        if v.valid():
            users = bundle_d.get('users')
            return ingest_data(sender, eos_client, conf['acl_contract'], users)
        else:
            return invalid_app()

    except InvalidSignature:
        return invalid_response()

    except Exception as e:
        logger.exception(e)
        return generic_error()
