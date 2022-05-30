from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_prefixed_env()

    from . import cards, manage
    app.register_blueprint(cards.blueprint)
    app.register_blueprint(manage.bp)
    
    return app

