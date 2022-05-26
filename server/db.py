import firebase_admin

from firebase_admin import credentials
from firebase_admin import firestore
from flask import current_app, g

def get_database():
    if 'db' not in g:
        creds = credentials.ApplicationDefault()
        firebase_admin.initialize_app(creds)
        g.db = firestore.client()
    
    return g.db
