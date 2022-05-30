import json
import re


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
