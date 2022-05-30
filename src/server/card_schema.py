from marshmallow import Schema, fields

class CardSchema(Schema):
    artist = fields.String()
    # border
    color_identity = fields.List(fields.String())
    colors = fields.List(fields.String())
    flavor = fields.String()
    # foreign_data
    # hand
    id = fields.UUID(required=True)
    image_url = fields.URL()
    # layout
    # legalities
    life = fields.Number()
    loyalty = fields.Number()
    mana_cost = fields.String()
    mana_value = fields.Number()
    multiverse_id = fields.Number()
    name = fields.String(required=True)
    names = fields.List(fields.String())
    number = fields.Number()
    original_text = fields.String()
    power = fields.Number()
    printings = fields.List(fields.String())
    rarity = fields.String()
    # release_date
    # reserved
    # rulings
    set = fields.String()
    set_name = fields.String()
    # source
    # starter
    subtypes = fields.List(fields.String())
    supertypes = fields.List(fields.String())
    text = fields.String()
    # timeshifted
    # toughness
    types = fields.List(fields.String())
    # variations
    # watermark