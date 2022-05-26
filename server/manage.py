import functools

from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)

bp = Blueprint('manage', __name__, url_prefix='/manage')

@bp.route('/liveness', methods=['GET'])
def liveness():
    data = { 'status': 'OKAY' }
    return data, 200

@bp.route('/readiness', methods=['GET'])
def readiness():
    data = { 'status': 'OKAY' }
    return data, 200
