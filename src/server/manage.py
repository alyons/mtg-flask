from curses import ERR
import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError

from .constants import ERROR_OBJ_NO_ENV_VARS
from .db import get_client

bp = Blueprint('manage', __name__, url_prefix='/manage')


@bp.route('/liveness', methods=['GET'])
def liveness():
    data = { 'status': 'OKAY' }
    return data, 200


def validate_mongo_variable(var: str) -> str | None:
    try:
        if not current_app.config["mongo"][var]:
            return f'Please ensure that FLASK_mongo__{var} is set to an appropriate value.'
    except KeyError:
        return f'Please ensure that FLASK_mongo__{var} is set to an appropriate value.'
        
    return None


@bp.route('/readiness', methods=['GET'])
def readiness():
    errors = []
    # Environment Variables Check
    try:
        if not current_app.config['mongo']:
            errors.append(ERROR_OBJ_NO_ENV_VARS)
    except KeyError:
            errors.append(ERROR_OBJ_NO_ENV_VARS)

    mongo_vars = ['username', 'password', 'url', 'authsource']
    errors.extend([{ 'message': 'Failed to read environment variable.', 'details': err } for err in [validate_mongo_variable(v) for v in mongo_vars] if not err == None])

    # Check Database Connectivity
    try:
        with get_client() as client:
            response = client['cards'].command('ping')

        if not response['ok'] == 1.0:
            errors.append({ 'message': 'Failed to ping MongoDB', 'details': response, 'suggestion': 'Validate your credentials' })
    except OperationFailure as err:
        errors.append({
            'message': 'Failed to ping database',
            'code': err.code,
            'details': err.details
        })
    except BaseException as err:
        errors.append({ 'message': 'Unknown Error', 'details': f'{err}' })

    if len(errors) > 0:
        return { 'status': 'FAILURE', 'errors': errors }, 500

    data = { 'status': 'OKAY' }
    return data, 200
