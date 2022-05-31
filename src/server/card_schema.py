from marshmallow import Schema, fields

VALID_FIELD_NAMES = [
    'artist', 
    'border', 
    'color_identity', 
    'colors', 
    'flavor', 
    'foreign_data', 
    'hand', 
    'id', 
    'image_url', 
    'layout', 
    'legalities', 
    'life', 
    'loyalty', 
    'mana_cost', 
    'mana_value', 
    'multiverse_id', 
    'name', 
    'names', 
    'number', 
    'original_text', 
    'power', 
    'printings', 
    'rarity', 
    'release_date', 
    'reserved', 
    'rulings', 
    'set', 
    'set_name', 
    'source', 
    'starter', 
    'subtypes', 
    'supertypes', 
    'text', 
    'timeshifted', 
    'toughness', 
    'types', 
    'variations', 
    'watermark', 
]

class CardSchema(Schema):
    artist = fields.String(default=None, allow_none=True)
    # border
    color_identity = fields.List(fields.String())
    colors = fields.List(fields.String())
    flavor = fields.String(default=None, allow_none=True)
    # foreign_data
    # hand
    id = fields.UUID(default=None, allow_none=True)
    image_url = fields.URL(default=None, allow_none=True)
    # layout
    # legalities
    life = fields.Number(default=None, allow_none=True)
    loyalty = fields.Number(default=None, allow_none=True)
    mana_cost = fields.String(default=None, allow_none=True)
    mana_value = fields.Number(default=None, allow_none=True)
    multiverse_id = fields.Number(default=None, allow_none=True)
    name = fields.String(default=None, allow_none=True)
    names = fields.List(fields.String(), allow_none=True)
    number = fields.Number(default=None, allow_none=True)
    original_text = fields.String(default=None, allow_none=True)
    power = fields.Number(default=None, allow_none=True)
    printings = fields.List(fields.String())
    rarity = fields.String(default=None, allow_none=True)
    # release_date
    # reserved
    # rulings
    set = fields.String(default=None, allow_none=True)
    set_name = fields.String(default=None, allow_none=True)
    # source
    # starter
    subtypes = fields.List(fields.String())
    supertypes = fields.List(fields.String())
    text = fields.String(default=None, allow_none=True)
    # timeshifted
    # toughness
    types = fields.List(fields.String())
    # variations
    # watermark