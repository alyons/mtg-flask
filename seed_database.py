import ast
import math
from typing import Any, Dict
import firebase_admin
import json
import pandas as pd

from firebase_admin import credentials
from firebase_admin import firestore
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

COLUMN_NAMES = ['name', 'multiverse_id', 'layout', 'names', 'mana_cost', 'cmc',
       'colors', 'color_identity', 'type', 'supertypes', 'subtypes', 'rarity',
       'text', 'flavor', 'artist', 'number', 'power', 'toughness', 'loyalty',
       'variations', 'watermark', 'border', 'timeshifted', 'hand', 'life',
       'reserved', 'release_date', 'starter', 'rulings', 'foreign_names',
       'printings', 'original_text', 'original_type', 'legalities', 'source',
       'image_url', 'set', 'set_name', 'id']

CARD_SUPER_TYPES = ['Basic', 'Legendary', 'Ongoing', 'Snow', 'World', 'Elite', 'Host']

console = Console()


def make_job_progress() -> Progress:
    job_progress = Progress(
        '{task.description}',
        SpinnerColumn(),
        BarColumn(),
        TextColumn('[progress.percentage]{task.percentage:>3.0f}%')
    )
    return job_progress

def try_parse_int(x, base=10, default_value=None):
    try:
        return int(x, base)
    except:
        return default_value


def parse_list(data_str: str):
    if type(data_str) is not str: return []

    items = data_str.replace('[', '').replace(']', '').split(',')
    return [i.strip().replace('\'', '') for i in items]


# TODO: Fix issue with json.loads not reading values from string
def try_json_loads(data, default_value=None):
    try:
        return json.loads(data)
    except:
        return default_value


def try_literal_eval(value: str, default_value=None):
    if type(value) is not str: return None
    try:
        return ast.literal_eval(value)
    except:
        return default_value


def parse_card_helper(key: str, value: Any) -> Any:
    match key:
        case 'life' | 'loyalty' | 'number' | 'power' | 'toughness' | 'cmc': return try_parse_int(value)
        case 'foreign_names' | 'legalities' | 'printings': return try_literal_eval(value)
        case 'colors' | 'color_identity' | 'variations' | 'subtypes'  | 'supertypes': return parse_list(value)
        case _: return None if type(value) == float and math.isnan(value) else value


def parse_card(card: pd.Series) -> Dict:
    output = card.to_dict()
    keys = card.keys()

    for k in keys:
        output[k] = parse_card_helper(k, output[k])

    # Parse all numeric values
    output['mana_value'] = output.pop('cmc')
    output['foreign_data'] = output.pop('foreign_names')

    # Special Parse for types
    card_type_str = output.pop('type')
    potential_types = card_type_str.split('—')[0].split()
    output['types'] = [t for t in potential_types if t not in CARD_SUPER_TYPES]

    return output


def print_dict(dict: Dict, keys=None):
    if keys == None: keys = dict.keys()
    for k in keys: print(f'\033[92m{k}\033[0m: {dict[k]}')


def load_cards():
    all_cards = pd.read_csv('/home/phoenix/projects/pokemon-flask-react/server/all_mtg_cards.csv')
    no_dupes = all_cards.drop_duplicates(subset='name')

    return no_dupes


def seed_database() -> None:
    console.print('Seed MtG Card Data')
    with console.status('Loading data from csv...'):
        data_frame = load_cards()
    console.print(f'Loaded {data_frame.size} unique cards!')

    cred = credentials.Certificate('/home/phoenix/projects/progression-website/.keys/sa_key.json')
    firebase_admin.initialize_app(cred)

    db = firestore.client()

    completed = 0
    total = data_frame.size
    job_progress = make_job_progress()
    task = job_progress.add_task(f'Uploading cards...', total=total)
    
    with console.status(job_progress):
        for _, row in data_frame.iterrows():
            card = parse_card(row)
            db.collection(u'mtg-cards').document(card['id']).set(card)
            completed += 1

            job_progress.update(task, completed=completed, description=f'Uploading cards...')
    
    console.print('Uploaded all cards!')


if __name__ == '__main__':
    seed_database()
