import functools

from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify)

from .db import get_database
from .constants import MTG_COLLECTION, REST_METHOD

blueprint = Blueprint('cards', __name__)

@blueprint.route('/cards', methods=['GET', 'POST'])
def cards():
    args = request.args
    if request.method == 'GET':
        db = get_database()
        cards_ref = db.collection(MTG_COLLECTION)
        query = cards_ref.order_by('name').limit(20)
        start_after = args.get('startafter')
        if start_after:
            query = query.start_after({ u'name': start_after })
        end_at = args.get('endat')
        if end_at:
            query = query.end_at({ u'name': end_at })
        result = [doc.to_dict() for doc in query.stream()]
        return jsonify(result), 200
