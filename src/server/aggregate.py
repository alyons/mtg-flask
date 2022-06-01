from flask import Blueprint, request
import json

from .db import get_client
from .mongodb_helper import build_filter
from .utils import generate_exception_response

blueprint = Blueprint('aggregate', __name__, url_prefix='/aggregate')

@blueprint.route('', methods=['GET'])
def get_aggregation():
    """Aggregate Get
    ---
    get:
      description: return an aggregation based on the pipeline
      parameters:
      - in: query
        name: pipeline
        description: MongoDB pipeline object to generate the data
      responses:
        200:
          content:
            application/json:
              schema: DatabaseResponse
    """
    pipeline = request.args.get('pipeline')

    try:
        with get_client() as client:
            collection = client['mtgSearchApp']['cards']
            cursor = collection.aggregate(pipeline=json.loads(pipeline))
            result = [c for c in cursor]

            return { 'status': 'OK', 'data': result }, 200
    except BaseException as err:
        return generate_exception_response('Failed to aggregate data', err), 500
