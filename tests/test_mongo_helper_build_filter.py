from server.mongodb_helper import build_filter


def test_empty_object():
    actual = build_filter('')
    assert actual == {}


def test_name_simple():
    actual = build_filter('name:Counter')
    assert actual == { 'name': { '$regex' : 'Counter', '$options': 'i' } }


def test_name_quoted():
    actual = build_filter('name:\'Liliana Vess\'')
    assert actual == { 'name': { '$regex' : 'Liliana Vess', '$options': 'i' } }


def test_text_simple():
    actual = build_filter('text:creatures')
    assert actual == { '$text': { '$search': 'creatures' } }


def test_text_quoted():
    actual = build_filter('text:\'put that card onto the battlefield\'')
    assert actual == { '$text': { '$search': "'put that card onto the battlefield'" } }


def test_mana_value():
    gte_actual = build_filter('mana_value>=3')
    assert gte_actual == { 'mana_value': { '$gte': 3 } }

    eq_actual = build_filter('mv=2')
    assert eq_actual == { 'mana_value': { '$eq': 2 } }

    lt_actual = build_filter('mana_value<5')
    assert lt_actual == { 'mana_value': { '$lt': 5 } }

