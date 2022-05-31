from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask import Blueprint

from .card_schema import CardSchema
from .response_schema import CardsResponseSchema, DatabaseResponseSchema, DistinctResponseSchema

spec = APISpec(
    title="MtG Search",
    version="1.0.0-alpha",
    openapi_version="3.0.2",
    info=dict(description="A Flask Based way to search through MtG Cards"),
    plugins=[FlaskPlugin(), MarshmallowPlugin()]
)

spec.components.schema('Card', schema=CardSchema)
spec.components.schema('CardsResponse', schema=CardsResponseSchema)
spec.components.schema('DatabaseResponse', schema=DatabaseResponseSchema)
spec.components.schema('DistinctResponse', schema=DistinctResponseSchema)

blueprint = Blueprint('spec', __name__)


@blueprint.route('/spec', methods=['GET'])
def get_specs():
    return spec.to_dict(), 200
