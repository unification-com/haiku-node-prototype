import flask

app = flask.Flask(__name__)
app.logger_name = "haiku-rpc"

logger = app.logger


def authorized_client(client_id, access_token):
    # TODO: Implement me
    return True


def encrypt_data(data):
    return data


def obtain_data(data_id):
    data = 'DATA'
    return encrypt_data(data)


@app.route('/data_request', methods=['POST'])
def data_request():
    d = flask.request.get_json()

    if not authorized_client(d['client_id'], d['access_token']):
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
            'result': obtain_data(d['data_id'])
        }
    )


if __name__ == '__main__':
    logger.info('Haiku RPC client started')
    app.run(debug=False, host="0.0.0.0", port=8050)
