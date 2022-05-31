import json
import re

from pymongo import ASCENDING, DESCENDING
from .colors import ColorFlag

TAG_REGEX = r'(name|text|mv|mana_?value|cmc|color|id|identity|format)(:!?|!?=|>=?|<=?)(\'.*\'|".*"|\S*)'
LOGICAL_REGEX = r'\s(AND|OR|NOT)\s'


def _op_comp_helper(op: str) -> str:
    match op:
        case ':' | '=': return '$eq'
        case '!=' | ':!': return '$ne'
        case '>': return '$gt'
        case '>=': return '$gte'
        case '<': return '$lt'
        case '<=': return '$lte'
        case _: return op


def _op_bit_helper(op: str) -> str:
    match op:
        case ':' | '=' | '>' | '>=' : return '$bitsAllSet'
        case ':!' | '!=' | '<' | '<=' : return '$bitsAllClear'
        case _: return op


def _color_tag(op: str, value: str) -> object:
    test = ColorFlag(value).flags

    match op:
        case '=': return { 'color_flag': { '$eq': test } }
        case '>=' | ':' : return { '$and': [{ 'color_flag': { _op_bit_helper(op): test } }, { 'color_flag': { '$gte': test } }] }
        case '>': return { '$and': [{ 'color_flag': { _op_bit_helper(op): test } }, { 'color_flag': { '$gt': test } }] }
        case _: return { 'color_flag': { _op_bit_helper(op): test } }


def _format_tag(value: str) -> object:
    return { 'legalities': { '$nin': [{ 'format': value, 'legality': 'Banned' }] }}


def _identity_tag(value: str) -> object:
    test = ColorFlag(value).flags
    inverse = ColorFlag(value).invert().flags

    return { '$and': [{ '$bitsAnySet': test}, { '$bitsAllClear': inverse }]}


def _mana_value_tag(op: str, value: str) -> object:
    return { 'mana_value': { _op_comp_helper(op): int(value) } }


def _name_tag(value: str) -> object:
    trimmed = value.replace("'", "").replace('"', '') # Remove quotes from around tag
    return { 'name': { '$regex' : f'{trimmed}', '$options': 'i' } }


def _text_tag(value: str) -> object:
    return { '$text': { '$search': value } }


def _parse_tag(tag: tuple[str, str, str]) -> object:
    print(tag)
    cat, op, value = tag
    
    match cat:
        case 'name': return _name_tag(value)
        case 'text': return _text_tag(value)
        case 'mv' | 'manavalue' | 'mana_value' | 'cmc': return _mana_value_tag(op, value)
        case 'color': return _color_tag(op, value)
        case 'id' | 'identity': return _identity_tag(value)
        case 'format': return _format_tag(value)
        case _: return { }


def _parse_tags(tag_str: str) -> object:
    tags = re.findall(TAG_REGEX, tag_str)

    if len(tags) == 0:
        return { }
    elif len(tags) == 1:
        return _parse_tag(tags[0])
    else:
        return { '$and': [_parse_tag(t) for t in tags] }


def _parse_expression(expression: str) -> object:
    # Add logic to break up expressions into smaller expressions until they are just tags
    return _parse_tags(expression)


def build_filter(filter: str) -> object:
    output = { }
    
    try:
        output = json.loads(filter)
        return output
    except ValueError: # If not a json, it might be using our filter language
        pass

    output = _parse_expression(filter)

    return output


def build_sort(sort: str) -> object:
    output = { }

    try:
        output = json.loads(sort)
        return output
    except ValueError: # If it's not a json, it might be using a kvp set up or something
        pass

    return output
