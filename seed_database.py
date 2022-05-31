import ast
import math
import json
import pandas as pd
import requests

from pymongo import UpdateMany
from pymongo.mongo_client import MongoClient
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from server.colors import ColorFlag


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


def parse_card_helper(key: str, value: any) -> any:
    match key:
        case 'life' | 'loyalty' | 'number' | 'power' | 'toughness' | 'cmc': return try_parse_int(value)
        case 'foreign_names' | 'legalities' | 'printings': return try_literal_eval(value)
        case 'colors' | 'color_identity' | 'variations' | 'subtypes'  | 'supertypes': return parse_list(value)
        case _: return None if type(value) == float and math.isnan(value) else value


def parse_card(card: pd.Series) -> dict:
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


def print_dict(dict: dict, keys=None):
    if keys == None: keys = dict.keys()
    for k in keys: print(f'\033[92m{k}\033[0m: {dict[k]}')


def load_cards():
    all_cards = pd.read_csv('all_mtg_cards.csv')
    no_dupes = all_cards.drop_duplicates(subset='name')

    return no_dupes


def seed_mongodb() -> None:
    console.print('Seed MtG Card Data')
    with console.status('Loading data from csv...'):
        data_frame = load_cards()
    console.print(f'Loaded {data_frame.size} unique cards!')

    with console.status('Parsing cards...'):
        cards = [parse_card(row) for _, row in data_frame.iterrows()]
    console.print('Parsed the cards!')
    
    with console.status('Batch writing to MongoDB...'):
        with MongoClient(f'mongodb://app:1uaV4WhBcoPXq6ZeT8W2@localhost:27017/?authSource=mtgSearchApp') as client:
            db = client['mtgSearchApp']
            db['cards'].insert_many(cards)

    console.print('Uploaded all cards!')


def add_color_and_identity_flags() -> None:
    console.print('Adding Color and Identity Flags')

    job_progress = make_job_progress()
    fetch_task_id = job_progress.add_task('Fetch Card Data', completed=0, total=1)

    projection = [ 'colors', 'color_identity', 'id' ]
    with console.status(job_progress):
        with MongoClient(f'mongodb://app:1uaV4WhBcoPXq6ZeT8W2@localhost:27017/?authSource=mtgSearchApp') as client:
            collection = client['mtgSearchApp']['cards']
            cursor = collection.find(projection=projection)
            cards = [c for c in cursor]
    
        job_progress.advance(fetch_task_id)
    console.print('Fetch Card Data... Complete!')
    
    color_updates: dict[ColorFlag, list[str]] = {}
    identity_updates: dict[ColorFlag, list[str]] = {}

    gen_task_id = job_progress.add_task('Generate Database Updates', completed=0, total=len(cards))

    with console.status(job_progress):
        for c in cards:
            color = ColorFlag(c['colors'])
            if not color in color_updates: color_updates[color] = []
            color_updates[color].append(c['id'])
            
            identity = ColorFlag(c['color_identity'])
            if not identity in identity_updates: identity_updates[identity] = []
            identity_updates[identity].append(c['id'])
            job_progress.advance(gen_task_id)
    
    console.print('Generate Database Updates... Complete!')

    update_task_id = job_progress.add_task('Update Cards', total=1)

    with console.status(job_progress):
        mongo_updates = []
        mongo_updates.extend([UpdateMany({ 'id': { '$in': color_updates[k]} }, [{ '$set': { 'color_flag': k.flags } }]) for k in color_updates])
        mongo_updates.extend([UpdateMany({ 'id': { '$in': identity_updates[k]} }, [{ '$set': { 'identity_flag': k.flags } }]) for k in identity_updates])
        with MongoClient(f'mongodb://app:1uaV4WhBcoPXq6ZeT8W2@localhost:27017/?authSource=mtgSearchApp') as client:
            collection = client['mtgSearchApp']['cards']
            result = collection.bulk_write(mongo_updates)
            # if result.acknowledged:
            #     console.print(result.bulk_api_result)
            # else:
            #     console.print('There was an error...')

        job_progress.advance(update_task_id)
    
    console.print('Update Cards... Complete!')


def update_release_date():
    console.print('Seed MtG Card Data')
    with console.status('Loading data from csv...'):
        data_frame = load_cards()
    console.print(f'Loaded {data_frame.size} unique cards!')

    with console.status('Parsing cards...'):
        cards = [parse_card(row) for _, row in data_frame.iterrows()]
    console.print('Parsed the cards!')

    console.print(cards[0]['release_date'])
            

if __name__ == '__main__':
    update_release_date()
