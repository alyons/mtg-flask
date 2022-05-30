from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify)
from marshmallow import INCLUDE
from pymongo import ASCENDING, DESCENDING
from uuid import uuid1

from .card_schema import CardSchema

from .db import get_client
from .query_builder import build_mongodb_query
from .utils import required_params, try_parse_int

LIMIT = 20
blueprint = Blueprint('cards', __name__)


@blueprint.route('/cards', methods=['POST'])
@required_params(CardSchema(unknown=INCLUDE))
def create_single_card():
    new_card = request.get_json()

    try:
        with get_client() as client:
            collection = client['mtgSearchApp']['cards']

            if not new_card['id'] == None:
                existing_card = collection.find_one({ 'id': new_card['id'] })
                if existing_card:
                    return { 'status': 'ERROR', 'message': 'Card already exists. Use PUT with /cards/<id> to update the card.' }, 400
            else:
                new_uuid = uuid1()
                existing_card = collection.find_one({ 'id': f'{new_uuid}' })
                while not existing_card == None:
                    new_uuid = uuid1()
                    existing_card = collection.find_one({ 'id': f'{new_uuid}' })
            
            existing_card = collection.find_one({ 'name': new_card['name'] })
            if existing_card:
                    return { 'status': 'ERROR', 'message': f'Card already exists. Use PUT with /cards/<id> to update the card.' }, 400
            
            result = collection.insert_one(new_card)
    except BaseException as err:
        print(f'Unhandled {type(err)=}: {err}')
        return jsonify(f'Unhandled {type(err)=}: {err}'), 500

    if result.acknowledged:
        return { 'status': 'OK', 'message': 'Card successfully inserted', 'id': new_card['id'] }, 201
    else:
        return { 'status': 'ERROR', 'message': 'Database write not acknowledged' }, 500


@blueprint.route('/cards', methods=['GET'])
def retrieve_multiple_cards():
    args = request.args

    # Insert logic to parse query here, including try catch for bad queries
    page = try_parse_int(args.get('page'), default_value=0)
    query_string = args.get('query')
    print(f'Query String: {query_string}')
    query = build_mongodb_query(query_string) if query_string and not query_string.isspace() else {}
    print(f'Query Object: {query}')

    try:
        with get_client() as client:
            collection = client['mtgSearchApp']['cards']
            results_count = collection.estimated_document_count() if query == {} else collection.count_documents(query)
            total_pages = (results_count // LIMIT) + (0 if results_count % LIMIT == 0 else 1)
            cursor = collection.find(query).sort('name', ASCENDING).skip(page * LIMIT).limit(LIMIT)
            result = [c for c in cursor]
            [r.pop('_id') for r in result]
            return jsonify({ 'cards': result, 'page': page, 'totalPages': total_pages }), 200
    except BaseException as err:
        print(f'Unhandled {type(err)=}: {err}')
        return jsonify(f'Unhandled {type(err)=}: {err}'), 500


@blueprint.route('/cards/<id>', methods=['GET'])
def retrieve_single_card(id):
    try:
        with get_client() as client:
            collection = client['mtgSearchApp']['cards']
            card = collection.find_one({ 'id': id })

        if not card:
            return { 'message': 'No card found' }, 404
        
        card.pop('_id')
        return card, 200
    except BaseException as err:
        return { 'error': f'{err}', 'message': 'Unknown error searching for card' }, 500


@blueprint.route('/cards/<id>', methods=['PUT'])
@required_params(CardSchema(unknown=INCLUDE))
def update_single_card(id):
    updated_card = request.get_json()
    try:
        with get_client() as client:
            collection = client['mtgSearchApp']['cards']
            result = collection.update_one({ 'id': id }, update={ '$set': updated_card })
    except BaseException as err:
        print(f'Unhandled {type(err)=}: {err}')
        return jsonify(f'Unhandled {type(err)=}: {err}'), 500
    
    if result.acknowledged and result.modified_count == 1:
        return { 'status': 'OK', 'message': 'Updated Card' }, 201
    else:
        return { 'status': 'ERROR', 'message': 'Failed to update card' }, 500


@blueprint.route('/cards/<id>', methods=['DELETE'])
def delete_single_card(id):
    try:
        with get_client() as client:
            collection = client['mtgSearchApp']['cards']
            result = collection.delete_one({ 'id': id })
            print(result)
            return { 'message': 'Card Deleted' }, 200
    except BaseException as err:
        return { 'error': f'{err}', 'message': 'Unknown error deleting for card' }, 500
