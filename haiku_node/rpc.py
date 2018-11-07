import flask
import hashlib

from cryptography.exceptions import InvalidSignature

from haiku_node.blockchain_helpers.eos.eosio_cleos import EosioCleos
from haiku_node.blockchain.eos.uapp import UnificationUapp
from haiku_node.data.factory import UnificationDataFactory
from haiku_node.encryption.payload import bundle, unbundle
from haiku_node.encryption.jwt.exceptions import (
    InvalidJWT, InvalidPublicKey, JWTSignatureMismatch)
from haiku_node.encryption.jwt.jwt import UnifJWT
from haiku_node.network.eos import (
    get_eos_rpc_client, get_cleos, get_ipfs_client)
from haiku_node.permissions.permission_batcher import PermissionBatcher
from haiku_node.permissions.permissions import UnifPermissions
from haiku_node.validation.validation import UnificationAppScValidation

app = flask.Flask(__name__)
app.logger_name = "haiku-rpc"

logger = app.logger


def invalid_response():
    return flask.jsonify({
        'success': False,
        'message': 'Unauthorized',
        'signature': None,
        'body': None
    }), 401


def invalid_jwt(message):
    return flask.jsonify({
        'success': False,
        'message': message,
        'signature': None,
        'body': None
    }), 401


def generic_error(message='Internal Server Error'):
    return flask.jsonify({
        'success': False,
        'message': message,
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


def error_request_self():
    return flask.jsonify({
        'success': False,
        'message': 'Cannot request data from self!',
        'signature': None,
        'body': None
    }), 418


def error_request_not_me():
    return flask.jsonify({
        'success': False,
        'message': 'Requested provider is not me',
        'signature': None,
        'body': None
    }), 418


def error_request_not_you():
    return flask.jsonify({
        'success': False,
        'message': 'You are not you...',
        'signature': None,
        'body': None
    }), 401


def bc_transaction_error():
    return flask.jsonify({
        'success': False,
        'message': 'Failed to write transaction to blockchain',
        'signature': None,
        'body': None
    }), 500


def obtain_data(keystore, eos_account_name, eos_client, acl_contract_acc,
                users, request_id=None):
    """
    :param eos_account_name: The account name of the requesting App (Data Consumer).
    :param eos_client: EOS RPC Client
    :param acl_contract_acc: The account name of the providing App (Data Provider).
    :param users: The users to obtain data for. None to get all available users
    :param request_id: Primary Key for the data request held in the Consumer's UApp smart contract
    """

    data_factory = UnificationDataFactory(
        eos_client, acl_contract_acc, eos_account_name, users)
    body = {
        'data': data_factory.get_raw_data()
    }

    d = bundle(keystore, acl_contract_acc, eos_account_name, body, 'Success')

    # load UApp SC for requesting app
    uapp_sc = UnificationUapp(eos_client, eos_account_name)
    # generate checksum
    data_hash = hashlib.sha224(str(d['payload']).encode('utf-8')).hexdigest()

    # temporarily allow acl_contract_acc@modreq to interact with consumer's contract
    eosio_cleos = EosioCleos(False)
    eosio_cleos.run(["set", "action", "permission", acl_contract_acc,
                     eos_account_name, 'updatereq', 'modreq', '-p', f'{acl_contract_acc}@active'])

    # write to Consumer's smart contract
    transaction_id = uapp_sc.update_data_request(request_id, acl_contract_acc, data_hash, "test")

    # Remove permission association for action in consumer's contract
    eosio_cleos.run(["set", "action", "permission", acl_contract_acc,
                     eos_account_name, 'updatereq', 'NULL', '-p', f'{acl_contract_acc}@active'])

    # check transaction has been processed
    if transaction_id is not None:
        return flask.jsonify(d), 200
    else:
        return bc_transaction_error()


def ingest_data(keystore, eos_account_name, eos_client, acl_contract_acc,
                users):
    response_body = {}

    d = bundle(
        keystore, acl_contract_acc, eos_account_name, response_body, 'Success')
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

        if sender == recipient:
            return error_request_self()

        bundle_d = unbundle(app.keystore, sender, d)

        eos_client = get_eos_rpc_client()

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
            request_id = bundle_d.get('request_id')

            # before processing data, check for any stashed permissions
            ipfs = get_ipfs_client()
            provider_uapp = UnificationUapp(eos_client, conf['acl_contract'])

            permissions = UnifPermissions(ipfs, provider_uapp)
            permissions.check_and_process_stashed(sender)

            return obtain_data(
                app.keystore, sender, eos_client, conf['acl_contract'],
                users, request_id)
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
        bundle_d = unbundle(app.keystore, sender, d)

        eos_client = get_eos_rpc_client()

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
            return ingest_data(
                app.keystore, sender, eos_client, conf['acl_contract'], users)
        else:
            return invalid_app()

    except InvalidSignature:
        return invalid_response()

    except Exception as e:
        logger.exception(e)
        return generic_error()


@app.route('/modify_permission', methods=['POST'])
def modify_permission():
    conf = app.unification_config

    try:
        d = flask.request.get_json()

        eos_perm = d['eos_perm']
        req_sender = d['user']
        jwt = d['jwt']

        cleos = get_cleos()
        eos_rpc_client = get_eos_rpc_client()

        # ToDo: find better way to get public key from EOS account
        public_key = cleos.get_public_key(req_sender, eos_perm)

        unif_jwt = UnifJWT(jwt, public_key)
        issuer = unif_jwt.get_issuer()
        audience = unif_jwt.get_audience()

        if audience != conf['acl_contract']:
            return error_request_not_me()

        if req_sender != issuer:
            return error_request_not_you()

        payload = unif_jwt.get_payload()

        # Check field list sent matches fields in metadata schema
        if len(payload['perms']) > 0:
            field_list = payload['perms'].split(',')

            uapp_sc = UnificationUapp(eos_rpc_client, conf['acl_contract'])
            db_schema = uapp_sc.get_db_schema_by_pkey(int(payload['schema_id']))

            if not db_schema:
                return generic_error(
                    f"Invalid Metadata Schema ID: {payload['schema_id']}")

            valid_fields = [f['name'] for f in db_schema['schema']['fields']]
            for pf in field_list:
                if pf not in valid_fields:
                    return generic_error(
                        f"Invalid field list: {payload['perms']}")

        batcher = PermissionBatcher()

        rowid = batcher.add_to_queue(issuer,
                                     payload['consumer'],
                                     payload['schema_id'],
                                     payload['perms'],
                                     payload['p_nonce'],
                                     payload['p_sig'],
                                     public_key)

        d = {
            'app': conf['acl_contract'],
            'proc_id': rowid
        }

        return flask.jsonify(d), 200

    except InvalidJWT as e:
        return invalid_jwt(e)

    except InvalidPublicKey as e:
        return invalid_jwt(e)

    except JWTSignatureMismatch as e:
        return invalid_jwt(e)

    except InvalidSignature:
        return invalid_response()

    except Exception as e:
        logger.exception(e)
        return generic_error()
