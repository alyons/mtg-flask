from server.colors import ColorFlag

def test_color_flag():
    br_str = ColorFlag('br')
    br_int = ColorFlag(0b00110)
    assert br_str == br_int

def test_color_flag_contains_valid():
    wg = ColorFlag(['white', 'GREEN'])
    w = ColorFlag('w')
    assert wg.contains(w)

def test_color_flag_factions():
    assert ColorFlag('izzet') == ColorFlag('ur')
    assert ColorFlag('golgari') == ColorFlag('witherbloom')
    assert ColorFlag('grixis').contains(ColorFlag('dimir'))

def test_color_flag_not_contains():
    witch = ColorFlag('witch')
    izzet = ColorFlag('izzet')
    assert not witch.contains(izzet)

def test_color_flag_shared():
    abzan = ColorFlag('abzan')
    temur = ColorFlag('temur')
    assert abzan.shared_colors(temur) == ColorFlag('g')

def test_color_flag_invert():
    bant = ColorFlag('bant')
    rakdos = bant.invert()
    assert rakdos == ColorFlag('br')
