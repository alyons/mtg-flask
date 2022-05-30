from server.utils import mana_value


def test_numeric_mana_cost():
    actual = mana_value('{2}') # Swiftfoot Boots
    assert actual == 2


def test_standard_mana_cost():
    actual = mana_value('{2}{B}{R}') # Wort, Boggart Auntie
    assert actual == 4


def test_hybrid_mana_cost():
    actual = mana_value('{4}{R/G}{R/G}') # Wort, Raidmother
    assert actual == 6


def test_x_mana_cost():
    actual = mana_value('{X}{X}{X}{R}{R}') # Crackle with Power
    assert actual == 2


def test_phyrexian_mana_cost():
    actual = mana_value('{3}{U/P}') # Tezzeret's Gambit
    assert actual == 4


def test_generic_hybrid_cost():
    actual = mana_value('{W/2}{u/2}{b/2}{r/2}{g/2}') # Reaper King
    assert actual == 10


def test_dismember():
    actual = mana_value('{1}{B/P}{B/P}')