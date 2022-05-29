from enum import Enum

MTG_COLLECTION = u'mtg-cards'

class REST_METHOD(Enum):
    GET     = 'GET'
    POST    = 'POST'
    PUT     = 'PUT'
    DELETE  = 'DELETE'
