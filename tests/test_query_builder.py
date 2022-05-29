from server.query_builder import build_mongodb_query


def test_empty_object():
    actual = build_mongodb_query('')
    assert actual == {}


def test_simple_name():
    actual = build_mongodb_query('name:Counter')
    assert actual == { 'name': { '$regex' : 'Counter', '$options': 'i' } }


def test_quoted_name():
    actual = build_mongodb_query('name:\'Liliana Vess\'')
    assert actual == { 'name': { '$regex' : 'Liliana Vess', '$options': 'i' } }


# def test_or_name():
#     actual = build_mongodb_query('name:Counter OR name:Force')
#     assert actual == { '$or': [
#         { 'name': { '$regex' : 'Counter', '$options': 'i' } },
#         { 'name': { '$regex' : 'Force', '$options': 'i' } }
#     ]}
