from enum import Enum

ERROR_OBJ_NO_ENV_VARS = {
    'message': 'Failed to read environment variables.',
    'details': '''
The application needs to be deployed with the following environment variables:
    - FLASK_mongo__authsource,
    - FLASK_mongo__username
    - FLASK_mongo__password
    - FLASK_mongo__url
''' }
