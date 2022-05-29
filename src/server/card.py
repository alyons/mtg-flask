from schematics.models import Model
from schematics.types import StringType, ListType, URLType

class Card(Model):
    name = StringType(required=True)
    image_url = URLType
