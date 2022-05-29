import functools

from copy import deepcopy
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify)
from pymongo.mongo_client import MongoClient
from pymongo import ASCENDING, DESCENDING

from .query_builder import build_mongodb_query
from .utils import try_parse_int

LIMIT = 20
blueprint = Blueprint('cards', __name__)


@blueprint.route('/cards', methods=['GET'])
def cards():
    if request.method == 'GET':
        args = request.args
        page = try_parse_int(args.get('page'), default_value=0)
        query_string = args.get('query')
        print(f'Query String: {query_string}')
        query = build_mongodb_query(query_string) if query_string and not query_string.isspace() else {}
        print(f'Query Object: {query}')

        # Insert logic to parse query here, including try catch for bad queries

        try:
            with MongoClient(f'mongodb://app:1uaV4WhBcoPXq6ZeT8W2@localhost:27017/?authSource=mtgSearchApp') as client:
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
