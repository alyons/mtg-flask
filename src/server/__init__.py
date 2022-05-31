from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_prefixed_env()

    from . import cards, docs, manage, spec
    app.register_blueprint(manage.bp)
    app.register_blueprint(cards.blueprint)
    with app.test_request_context():
        spec.spec.path(view=cards.post_single_card)
        spec.spec.path(view=cards.get_multiple_cards)
        spec.spec.path(view=cards.get_single_card)
        spec.spec.path(view=cards.put_single_card)
        spec.spec.path(view=cards.delete_single_card)
        spec.spec.path(view=cards.get_distinct_values_for_key)
    app.register_blueprint(spec.blueprint)
    app.register_blueprint(docs.doc_blueprint)
    
    return app
