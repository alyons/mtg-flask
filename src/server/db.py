from flask import current_app, g
from pymongo.mongo_client import MongoClient

def get_client() -> MongoClient:
    if 'client' not in g:
        g.client = MongoClient(get_connection_string())

    return g.client

def get_connection_string() -> str:
    return f'mongodb://{current_app.config["mongo"]["username"]}:{current_app.config["mongo"]["password"]}@{current_app.config["mongo"]["url"]}/?authSource={current_app.config["mongo"]["authsource"]}'
