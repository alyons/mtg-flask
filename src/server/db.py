from pymongo.mongo_client import MongoClient
from pymongo.database import Database

from flask import current_app, g


def get_db() -> Database:
    if 'db' not in g:
        client = MongoClient(f'mongodb://mtgSearchApp:1uaV4WhBcoPXq6ZeT8W2@localhost:27017/?authSource=admin')
        g.db = client.mtgSearch

    return g.db