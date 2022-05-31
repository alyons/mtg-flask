from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/docs'
# API_URL = 'http://petstore.swagger.io/v2/swagger.json'
API_URL = '/spec'

doc_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'MtG Search Flask'
    }
)
