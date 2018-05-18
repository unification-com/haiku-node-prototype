import flask

from haiku_node.config.keys import get_public_key
from haiku_node.validation.encryption import verify_request, sign_request

app = flask.Flask(__name__)
app.logger_name = "haiku-rpc"

logger = app.logger


def verify_account(eos_account_name, body, signature) -> bool:
    logger.info(f"Attempting to authorize {eos_account_name}")
    return verify_request(get_public_key(eos_account_name), body, signature)


def obtain_data(body):
    data = 'DATA'
    return data


def sign_data(body):
    keystore = getattr(app, 'keystore')
    private_key = keystore.get_rpc_auth_private_key()
    return sign_request(private_key, body)


@app.route('/data_request', methods=['POST'])
def data_request():
    d = flask.request.get_json()

    if not verify_account(d['eos_account_name'], d['body'], d['signature']):
        return flask.jsonify({
                'success': False,
                'message': 'Unauthorized',
                'signature': None,
                'body': None
            }), 401

    data = obtain_data(d['body'])

    return flask.jsonify({
            'success': True,
            'message': 'Success',
            'signature': sign_data(data),
            'body': data
        }), 200


if __name__ == '__main__':
    logger.info('Haiku RPC client started')
    app.run(debug=False, host="0.0.0.0", port=8050)
