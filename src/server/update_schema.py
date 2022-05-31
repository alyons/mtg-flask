from marshmallow import Schema, fields

class UpdateBodySchema(Schema):
    filter = fields.Raw(required=True)
    update = fields.Raw(required=True)
