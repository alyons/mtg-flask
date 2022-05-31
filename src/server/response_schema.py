from marshmallow import Schema, fields
from .card_schema import CardSchema

class CardsResponseSchema(Schema):
    status = fields.String(required=True)
    cards = fields.List(fields.Nested(CardSchema), required=True)
    page = fields.Integer(optional=True)
    totalPages = fields.Integer(optional=True)


class DatabaseResponseSchema(Schema):
    status = fields.String(required=True)
    message = fields.String(optional=True)
    details = fields.List(fields.String(), optional=True)


class DistinctResponseSchema(Schema):
    status = fields.String(required=True)
    key = fields.String()
    data = fields.List(fields.String())
