from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify)
from marshmallow import INCLUDE
from pymongo import ASCENDING, DESCENDING
from uuid import uuid1
import json

from .card_schema import CardSchema, VALID_FIELD_NAMES
from .response_schema import CardsResponseSchema, DatabaseResponseSchema
from .update_schema import UpdateBodySchema

from .db import get_client
from .mongodb_helper import build_filter, build_sort
from .utils import required_params, try_parse_int, generate_exception_response

DEFAULT_LIMIT = 20
blueprint = Blueprint('cards', __name__, url_prefix='/cards')


@blueprint.route('', methods=['POST'])
@required_params(CardSchema(unknown=INCLUDE))
def post_single_card():
    """Card Post
    ---
    post:
      description: Create a new card
      parameters:
      - in: body
        name: body
        schema: CardSchema
      responses:
        200:
          content:
            application/json:
              schema: DatabaseResponse
    """
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


@blueprint.route('', methods=['GET'])
def get_multiple_cards():
    """Cards Get
    ---
    get:
      description: return a list of all of the cards
      parameters:
      - in: query
        name: filter
        description: Filter out cards based on specific criteria
      - in: query
        name: projection
        description: Return only specified parameters
      - in: query
        name: page
        description: Enable Pagination and get the appropriate data
      - in: query
        name: sort
        description: Sort the data by certain fields
      - in: query
        name: order
        description: Change the order of the sort
      responses:
        200:
          content:
            application/json:
              schema: CardsResponse
    """
    args = request.args
    
    filter = {}
    projection = None
    skip = 0
    limit = 0
    order = ASCENDING
    sort = [('name', order )]

    if args.get('filter'):
        filter = build_filter(args.get('filter'))

    if args.get('projection'):
        projection = [p for p in args.get('projection').split(',') if p in VALID_FIELD_NAMES]
    
    if args.get('page'):
        print(f"Page: {args.get('page')}")
        limit = DEFAULT_LIMIT
        skip = (try_parse_int(args.get('page'), default_value=1) - 1) * limit

    if args.get('order'):
        if args.get('order').lower() == 'descending' or args.get('order') == -1:
            order = DESCENDING

    if args.get('sort') and args.get('sort') in ['name', 'set', 'mana_value']:
        sort = [(args.get('sort'), order)]
        if args.get('sort') == 'set':
            sort.append(('set_number', ASCENDING))

    try:
        with get_client() as client:
            collection = client['mtgSearchApp']['cards']
            if args.get('page'):
                results_count = collection.estimated_document_count() if filter == {} else collection.count_documents(filter)
                total_pages = (results_count // limit)
            cursor = collection.find(filter=filter, projection=projection, skip=skip, limit=limit, sort=sort)
            result = [c for c in cursor]
            [r.pop('_id') for r in result]
        
        output = { 'status': 'OK', 'cards': result }
        if args.get('page'):
            output['page'] = args.get('page')
            output['totalPages'] = total_pages

        return output, 200
    except BaseException as err:
        return generate_exception_response('Failed to get cards', err), 500


@blueprint.route('/<id>', methods=['GET'])
def get_single_card(id):
    """Card Get
    ---
    get:
      description: Get a single card
      parameters:
      - in: path
        name: id
      responses:
        200:
          content:
            application/json:
              schema: CardsResponse
    """
    try:
        with get_client() as client:
            collection = client['mtgSearchApp']['cards']
            card = collection.find_one({ 'id': id })

        if not card:
            return { 'message': 'No card found' }, 404
        
        card.pop('_id')
        output = { 'status': 'OK', 'cards': [card] }
        return output, 200
    except BaseException as err:
        return generate_exception_response(f'Failed to get card with id: {id}'), 500


# !!! --- NOT WORKING --- !!!
# @blueprint.route('', methods = ['PUT'])
# @required_params(UpdateBodySchema())
# def put_multiple_cards():
#     body = request.get_json()
#     try:
#         with get_client() as client:
#             collection = client['mtgSearchApp']['cards']
#             result = collection.update_many(body['filter'], body['update'])
#     except BaseException as err:
#         return generate_exception_response(f'Failed to update cards'), 500
    
#     if result.acknowledged:
#         return { 'status': 'OK', 'message': 'Update run successfully', 'details': result }, 201
#     else:
#         return { 'status': 'ERROR', 'message': 'Failed to update cards', 'details': f'{result}' }, 500


@blueprint.route('/<id>', methods=['PUT'])
@required_params(CardSchema(unknown=INCLUDE))
def put_single_card(id):
    """Card Put
    ---
    put:
      description: Update a single card
      parameters:
      - in: path
        name: id
      - in: body
        name: body
        schema: CardSchema
      responses:
        200:
          content:
            application/json:
              schema: DatabaseResponse
    """
    updated_card = request.get_json()
    try:
        with get_client() as client:
            collection = client['mtgSearchApp']['cards']
            result = collection.update_one({ 'id': id }, update={ '$set': updated_card })
    except BaseException as err:
        return generate_exception_response(f'Failed to update card with id: {id}'), 500
    
    if result.acknowledged and result.modified_count == 1:
        return { 'status': 'OK', 'message': 'Updated Card' }, 201
    else:
        return { 'status': 'ERROR', 'message': 'Failed to update card' }, 500


@blueprint.route('/<id>', methods=['DELETE'])
def delete_single_card(id):
    """Card Delete
    ---
    delete:
      description: Delete a single card
      parameters:
      - in: path
        name: id
      responses:
        200:
          content:
            application/json:
              schema: DatabaseResponse
    """
    try:
        with get_client() as client:
            collection = client['mtgSearchApp']['cards']
            result = collection.delete_one({ 'id': id })
            return { 'status': 'OK', 'message': 'Card Deleted', 'details': result }, 200
    except BaseException as err:
        return generate_exception_response(f'Failed to delete card with id: {id}', err), 500


# Some Helper Calls for distinct calls and the like
@blueprint.route('/distinct/<key>', methods=['GET'])
def get_distinct_values_for_key(key):
    """Card Distinct Get
    ---
    get:
      description: Get the distinct values for a certain key in the database
      parameters:
      - in: path
        name: key
      responses:
        200:
          content:
            application/json:
              schema: DatabaseResponse
    """
    allowed_keys = ['colors', 'color_identity', 'mana_cost']
    if not key in allowed_keys:
        return { 'status': 'ERROR', 'message': 'The only keys allowed are: {allowed_keys}' }, 400
    
    try:
        with get_client() as client:
            collection = client['mtgSearchApp']['cards']
            result = collection.distinct(key)
        
        return { 'status': 'OK', 'key': key, 'data': result }, 200
    except BaseException as err:
        return generate_exception_response(f'Failed to delete card with id: {id}', err), 500
