import flask
import json

from cryptography.exceptions import InvalidSignature
from eosapi import Client

from haiku_node.config.keys import get_public_key
from haiku_node.validation.encryption import (
    verify_request, sign_request, encrypt, decrypt)

from haiku_node.validation.validation import UnificationAppScValidation

app = flask.Flask(__name__)
app.logger_name = "haiku-rpc"

logger = app.logger


def verify_account(eos_account_name: str, body, signature):
    verify_request(get_public_key(eos_account_name), body, signature)


def sign_data(body):
    private_key = app.keystore.get_rpc_auth_private_key()
    return sign_request(private_key, body)


def decrypt_data(body):
    private_key = app.keystore.get_rpc_auth_private_key()
    return decrypt(private_key, body)


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


def obtain_data(body, eos_account_name):
    """
    :param body: A request for a particular set of data.
    :param eos_account_name: The account name of the requesting App.
    """
    data = 'DATA'
    encrypted_data = encrypt(get_public_key(eos_account_name), data)

    return flask.jsonify({
        'success': True,
        'message': 'Success',
        'signature': sign_data(data),
        'body': encrypted_data
    }), 200


def ingest_data(body):
    # TODO: The response body needs to be signed before jsonified

    response_body = "body"
    return flask.jsonify({
        'success': True,
        'message': 'Success',
        'signature': sign_data(response_body),
        'body': response_body
    }), 200


@app.route('/data_request', methods=['POST'])
def data_request():
    try:
        d = flask.request.get_json()
        verify_account(
            d['eos_account_name'], json.dumps(d['body']), d['signature'])

        # Validate requesting app against smart contracts
        # config is this Haiku Node's config fle, containing its ACL/Meta Data
        # Smart Contract account/address and the EOS RPC server/port used for
        # communicating with the blockchain.
        conf = app.unification_config

        # Init the validation class for THIS Haiku, and validate the
        # REQUESTING APP. Since we only need to validate the app at this point,
        # set get_perms=False

        eos_client = Client(
            nodes=[f"http://{conf['eos_rpc_ip']}:{conf['eos_rpc_port']}"])
        v = UnificationAppScValidation(
            eos_client, conf['acl_contract'], d['eos_account_name'],
            get_perms=True)

        # If the REQUESTING APP is valid according to MOTHER, then we can
        # generate the data. If not, return an invalid_app response
        # Whatever obtain_data eventually uses to grab the data will also need
        # to load the UnificationAppScValidation class, so it knows which users
        # have granted permissions to the REQUESTING APP, and get the correct
        # data
        if v.valid_code():
            data_for_user = d['body']['user']
            has_perm = v.app_has_user_permission(data_for_user)
            if has_perm:
                return obtain_data(d['body'], d['eos_account_name'])
            else:
                return unauthorized_for_user()
        else:
            return invalid_app()

    except InvalidSignature:
        return invalid_response()


@app.route('/data_ingest', methods=['POST'])
def data_ingest():
    try:
        d = flask.request.get_json()
        decrypted_body = decrypt_data(d['body'])
        verify_account(d['eos_account_name'], decrypted_body, d['signature'])
        return ingest_data(decrypted_body)

    except InvalidSignature:
        return invalid_response()

    except Exception as e:
        logger.exception(e)
        return generic_error()
