import flask

from haiku_node.config.keys import get_public_key
from haiku_node.validation.encryption import verify_request

app = flask.Flask(__name__)
app.logger_name = "haiku-rpc"

logger = app.logger


def authorized_client(eos_account_name, body, signature):
    logger.info(f"Attempting to authorize {eos_account_name}")

    public_key = get_public_key(eos_account_name)
    return verify_request(public_key, body, signature)


def encrypt_data(data):
    return data


def obtain_data(body):
    data = 'DATA'
    return encrypt_data(data)


@app.route('/data_request', methods=['POST'])
def data_request():
    d = flask.request.get_json()

    if not authorized_client(d['eos_account_name'], d['body'], d['signature']):
        return flask.jsonify(
            {
                'success': False,
                'message': 'Unauthorized',
                'result': None
            }
        )

    return flask.jsonify(
        {
            'success': True,
            'message': 'Success',
            'result': obtain_data(d['body'])
        }
    )


if __name__ == '__main__':
    logger.info('Haiku RPC client started')
    app.run(debug=False, host="0.0.0.0", port=8050)
