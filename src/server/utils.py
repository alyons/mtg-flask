import json
import re
from marshmallow import Schema, ValidationError
from functools import wraps
from flask import request

FORMAT_NAMES = [
    'Alchemy',
    'Brawl',
    'Commander',
    'Duel',
    'Explorer',
    'Future',
    'Gladiator',
    'Historic',
    'Historicbrawl',
    'Legacy',
    'Modern',
    'Oldschool',
    'Pauper',
    'Paupercommander',
    'Penny',
    'Pioneer',
    'Premodern',
    'Standard',
    'Vintage'
]

FACTION_COLOR_DICT = {
    'colorless': '',
    'devoid': '',
    'white': 'w',
    'blue': 'u',
    'black': 'b',
    'red': 'r',
    'green': 'g',
    'azorius': 'wu',
    'boros': 'rw',
    'dimir': 'ub',
    'golgari': 'bg',
    'gruul': 'rg',
    'izzet': 'ur',
    'orzhov': 'wb',
    'rakdos': 'rb',
    'selesnya': 'wg',
    'simic': 'ug',
    'abzan': 'wbg',
    'bant': 'wug',
    'esper': 'wub',
    'grixis': 'urb',
    'jeskai': 'wur',
    'jund': 'brg',
    'mardu': 'wbr',
    'naya': 'wgr',
    'sultai': 'ubg',
    'temur': 'urg',
    'glint': 'ubrg',
    'dune': 'wbrg',
    'ink': 'wurg',
    'witch': 'wubg',
    'yore': 'wubr',
    'silverquill': 'bw',
    'prismari': 'ub',
    'witherbloom': 'bg',
    'lorehold': 'rw',
    'quandrix': 'gu'
}


def try_parse_int(x, base=10, default_value=None):
    try:
        return int(x, base)
    except:
        return default_value


def safe_serialize(obj):
    default = lambda o: f'<<non-serializable: {type(o).__qualname__}>>'
    return json.dumps(obj, default=default)


def characterToColor(char: str) -> str:
    match char.lower():
        case 'w': return 'White'
        case 'u': return 'Blue'
        case 'b': return 'Black'
        case 'r': return 'Red'
        case 'g': return 'Green'
        case _: return None


def invert_colors(colors: str) -> list[str]:
    output = ['White', 'Blue', 'Black', 'Red', 'Green']
    
    [output.remove(characterToColor(c)) for c in colors]

    return output


MANA_REGEX = r'\{(\d+|[wubrgx])\/?([wubrgp2])?\}'

def _parse_symbol_value(symbol: tuple[str, str]) -> int:
    match symbol[1].lower():
        case '2': return 2
        case 'p': return 1
    
    match symbol[0].lower():
        case 'x': return 0
        case 'w' | 'u' | 'b' | 'r' | 'g': return 1
        case s: return try_parse_int(s, default_value=1)


def mana_value(mana_cost: str) -> int:
    mana_symbols = re.findall(MANA_REGEX, mana_cost, re.IGNORECASE)
    # print(mana_symbols)
    values = [_parse_symbol_value(s) for s in mana_symbols]
    return sum(values)


def required_params(schema: Schema):
    def decorator(fn):

        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                schema.load(request.get_json())
            except ValidationError as err:
                return { 'status': 'ERROR', 'details': err.messages }, 400

            return fn(*args, **kwargs)
        
        return wrapper
    return decorator


def double_check_color(value: str, control: str) -> bool:
    if control.lower() == value.lower(): return True

    if control.lower() == 'w' and value.lower() == 'white': return True
    if control.lower() == 'u' and value.lower() == 'blue': return True
    if control.lower() == 'b' and value.lower() == 'black': return True
    if control.lower() == 'r' and value.lower() == 'red': return True
    if control.lower() == 'g' and value.lower() == 'green': return True

    return False


def generate_exception_response(message: str, err: BaseException = None) -> object:
    response = { 'status': 'ERROR', 'message': message }
    if err: response['details'] = f'Unhandled {type(err)=}: {err}'
    return response
