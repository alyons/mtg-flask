import re

from pymongo import ASCENDING, DESCENDING
from .utils import characterToColor, invert_colors

TAG_REGEX = r'(name)(:)(\'.*\'|".*"|\S*)'
OPERATOR_REGEX = r'(AND|OR|NOT)'


def _name_tag(value: str) -> object:
    trimmed = value.replace("'", "").replace('"', '') # Remove quotes from around tag
    return { 'name': { '$regex' : f'{trimmed}', '$options': 'i' } }


def _parse_tag(tag: str) -> object:
    tag_matches = re.search(TAG_REGEX, tag)
    if tag_matches == None or len(tag_matches.groups()) != 3:
        return {}
    
    cat, op, value = tag_matches.groups()
    
    match cat:
        case 'name': return _name_tag(value)
        case _: return {}


def _parse_expression(expression: str) -> object:
    return _parse_tag(expression)


def build_mongodb_query(query_string: str) -> object:
    query = _parse_expression(query_string)

    return query
