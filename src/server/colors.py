from .utils import double_check_color, FACTION_COLOR_DICT


class ColorFlag():
    WHITE_BIT = 0b10000
    BLUE_BIT  = 0b01000
    BLACK_BIT = 0b00100
    RED_BIT   = 0b00010
    GREEN_BIT = 0b00001
    COLOR_CHAR_ARRAY = ['w', 'u', 'b', 'r', 'g']

    def __init__(self: 'ColorFlag', colors: str | list[str] | int) -> None:
        # if isinstance(colors, str):
        self.flags = 0
        if isinstance(colors, int): self.flags = colors
        if isinstance(colors, str):
            if colors in FACTION_COLOR_DICT.keys():
                self.flags = ColorFlag._color_flag_from_str(FACTION_COLOR_DICT[colors])
            else:
                self.flags = ColorFlag._color_flag_from_str(colors)
        if isinstance(colors, list): self.flags = ColorFlag._color_flag_from_list(colors)

    @classmethod
    def _color_flag_from_str(cls: 'ColorFlag', colors: str) -> int:
        bits = ''.join(['1' if c in colors.lower() else '0' for c in ColorFlag.COLOR_CHAR_ARRAY])
        return int(bits, 2)
    
    @classmethod
    def _color_flag_from_list(cls: 'ColorFlag', colors: list[str]) -> int:
        test = [t.lower() for t in colors]
        bits = ''.join(['1' if any(double_check_color(t, c) for t in test) else '0' for c in ColorFlag.COLOR_CHAR_ARRAY])
        return int(bits, 2)

    def __eq__(self: 'ColorFlag', other: 'ColorFlag') -> bool:
        if not isinstance(other, ColorFlag): return False
        return self.flags == other.flags
    
    def contains(self: 'ColorFlag', other: 'ColorFlag') -> bool:
        if not isinstance(other, ColorFlag): return False
        if other.iscolorless(): return False
        if self == other: return True
        if self.flags > other.flags and self.flags & other.flags == other.flags: return True
        return False
    
    def shared_colors(self: 'ColorFlag', other: 'ColorFlag') -> 'ColorFlag':
        return ColorFlag(self.flags & other.flags)
    
    def invert(self: 'ColorFlag') -> 'ColorFlag':
        if not self.iscolorless(): return ColorFlag(~self.flags & 0b11111)

    def __str__(self: 'ColorFlag') -> str:
        output = ''
        if self.flags & ColorFlag.WHITE_BIT > 0: output += 'w'
        if self.flags & ColorFlag.BLUE_BIT > 0:  output += 'u'
        if self.flags & ColorFlag.BLACK_BIT > 0: output += 'b'
        if self.flags & ColorFlag.RED_BIT > 0:   output += 'r'
        if self.flags & ColorFlag.GREEN_BIT > 0: output += 'g'
        return output
    
    def __hash__(self: 'ColorFlag'):
        return hash(self.flags)
    
    def iscolorless(self: 'ColorFlag') -> bool:
        return self.flags == 0
