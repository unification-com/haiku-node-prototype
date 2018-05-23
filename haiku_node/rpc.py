import flask

from cryptography.exceptions import InvalidSignature

from haiku_node.config.keys import get_public_key
from haiku_node.validation.encryption import (
    verify_request, sign_request, encrypt, decrypt)

app = flask.Flask(__name__)
app.logger_name = "haiku-rpc"

logger = app.logger


def verify_account(eos_account_name, body, signature):
    verify_request(get_public_key(eos_account_name), body, signature)


def sign_data(body):
    keystore = getattr(app, 'keystore')
    private_key = keystore.get_rpc_auth_private_key()
    return sign_request(private_key, body)


def decrypt_data(body):
    keystore = getattr(app, 'keystore')
    private_key = keystore.get_rpc_auth_private_key()
    return decrypt(private_key, body)


def invalid_response():
    return flask.jsonify({
        'success': False,
        'message': 'Unauthorized',
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
        verify_account(d['eos_account_name'], d['body'], d['signature'])
        return obtain_data(d['body'], d['eos_account_name'])

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


if __name__ == '__main__':
    logger.info('Haiku RPC client started')
    app.run(debug=False, host="0.0.0.0", port=8050)
