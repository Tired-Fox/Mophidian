from __future__ import annotations
from typing import Callable


def color(*args, **kwargs) -> str:
    """Takes prefix and suffix ansi color codes to style the args.

        Keyword Args:
            prefix list[int]: The prefix ansi color codes
            suffix list[int]: The suffix ansi color codes
    Returns:
        str: The formatted string
    """
    prefix: str = f"\x1b[{';'.join(kwargs['prefix'])}m" if "prefix" in kwargs else ""
    suffix: str = (
        f"\x1b[{';'.join(kwargs['suffix'])}m"
        if "suffix" in kwargs
        else f"\x1b[{FColor.RESET};{BColor.RESET}m"
    )
    return f"{prefix}{''.join([str(arg) for arg in args])}{suffix}"


def url(url: str, title: str = None) -> str:
    """Format a url with an optional title to get an ansi url link for the terminal.

    Args:
        url (str): The url to use in the link
        title (str, optional): The title to display. Defaults to None.

    Returns:
        str: Formatted ansi clickable link
    """
    if title is None:
        title = url

    return f'\x1b]8;;{url}\x1b\\{color(title, prefix=[Style.BOLD, Style.UNDERLINE], suffix=[Style.NOBOLD, Style.NOUNDERLINE])}\x1b]8;;\x1b\\'


class FColor:
    """Ansi color codes for foreground text color.

    Options:
    - BLACK
    - RED
    - GREEN
    - YELLOW
    - BLUE
    - MAGENTA
    - CYAN
    - WHITE
    - RESET
    """

    BLACK: str = "30"
    """(30) Red ansi code"""
    RED: str = "31"
    """(31) Red ansi code"""
    GREEN: str = "32"
    """(32) Green ansi code"""
    YELLOW: str = "33"
    """(33) Yellow ansi code"""
    BLUE: str = "34"
    """(34) Blue ansi code"""
    MAGENTA: str = "35"
    """(35) Magenta ansi code"""
    CYAN: str = "36"
    """(36) Cyan ansi code"""
    WHITE: str = "37"
    """(37) White ansi code"""
    RGB: Callable = lambda r, g, b: f"38;{r};{g};{b}"
    """(38) RGB Color ansi code"""
    XTERM: Callable = lambda x: f"38;5;{x}"
    """(38;5) Color xterm code"""
    RESET: str = "39"
    """(39) Reset Color ansi code"""


class BColor:
    """Ansi color codes for background text color.

    Options:
    - BLACK
    - RED
    - GREEN
    - YELLOW
    - BLUE
    - MAGENTA
    - CYAN
    - WHITE
    - RESET
    """

    BLACK: str = "40"
    """(40) Red ansi code"""
    RED: str = "41"
    """(41) Red ansi code"""
    GREEN: str = "42"
    """(42) Green ansi code"""
    YELLOW: str = "43"
    """(43) Yellow ansi code"""
    BLUE: str = "44"
    """(44) Blue ansi code"""
    MAGENTA: str = "45"
    """(45) Magenta ansi code"""
    CYAN: str = "46"
    """(46) Cyan ansi code"""
    WHITE: str = "47"
    """(47) White ansi code"""
    RGB: Callable = lambda r, g, b: f"48;{r};{g};{b}"
    """(48) RGB Color ansi code"""
    XTERM: Callable = lambda x: f"48;5;{x}"
    """(48;5) Color xterm code"""
    RESET: str = "49"
    """(49) Reset Color ansi code"""


class Style:
    """Ansi color codes for test style.

    Options:
    - BOLD
    - NOBOLD
    - UNDERLINE
    - NOUNDERLINE
    """

    BOLD: str = "1"
    """(1) Bold ansi code"""
    NOBOLD: str = "22"
    """(22) No Bold ansi code"""
    UNDERLINE: str = "4"
    """(4) Underline ansi code"""
    NOUNDERLINE: str = "24"
    """(24) No Underline ansi code"""


RESET = "0"


class XTerm:
    """XTerm color codes

    See this site for examples: https://www.ditig.com/256-colors-cheat-sheet
    """

    Black: int = 0
    """(0) Xterm color code"""
    Maroon: int = 1
    """(1) Xterm color code"""
    Green: int = 2
    """(2) Xterm color code"""
    Olive: int = 3
    """(3) Xterm color code"""
    Navy: int = 4
    """(4) Xterm color code"""
    Purple: int = 5
    """(5) Xterm color code"""
    Teal: int = 6
    """(6) Xterm color code"""
    Silver: int = 7
    """(7) Xterm color code"""
    Grey: int = 8
    """(8) Xterm color code"""
    Red: int = 9
    """(9) Xterm color code"""
    Lime: int = 10
    """(10) Xterm color code"""
    Yellow: int = 11
    """(11) Xterm color code"""
    Blue: int = 12
    """(12) Xterm color code"""
    Fuchsia: int = 13
    """(13) Xterm color code"""
    Aqua: int = 14
    """(14) Xterm color code"""
    White: int = 15
    """(15) Xterm color code"""
    Grey0: int = 16
    """(16) Xterm color code"""
    NavyBlue: int = 17
    """(17) Xterm color code"""
    DarkBlue: int = 18
    """(18) Xterm color code"""
    Blue3: int = 19
    """(19) Xterm color code"""
    Blue3: int = 20
    """(20) Xterm color code"""
    Blue1: int = 21
    """(21) Xterm color code"""
    DarkGreen: int = 22
    """(22) Xterm color code"""
    DeepSkyBlue4: int = 23
    """(23) Xterm color code"""
    DeepSkyBlue4: int = 24
    """(24) Xterm color code"""
    DeepSkyBlue4: int = 25
    """(25) Xterm color code"""
    DodgerBlue3: int = 26
    """(26) Xterm color code"""
    DodgerBlue2: int = 27
    """(27) Xterm color code"""
    Green4: int = 28
    """(28) Xterm color code"""
    SpringGreen4: int = 29
    """(29) Xterm color code"""
    Turquoise4: int = 30
    """(30) Xterm color code"""
    DeepSkyBlue3: int = 31
    """(31) Xterm color code"""
    DeepSkyBlue3: int = 32
    """(32) Xterm color code"""
    DodgerBlue1: int = 33
    """(33) Xterm color code"""
    Green3: int = 34
    """(34) Xterm color code"""
    SpringGreen3: int = 35
    """(35) Xterm color code"""
    DarkCyan: int = 36
    """(36) Xterm color code"""
    LightSeaGreen: int = 37
    """(37) Xterm color code"""
    DeepSkyBlue2: int = 38
    """(38) Xterm color code"""
    DeepSkyBlue1: int = 39
    """(39) Xterm color code"""
    Green3: int = 40
    """(40) Xterm color code"""
    SpringGreen3: int = 41
    """(41) Xterm color code"""
    SpringGreen2: int = 42
    """(42) Xterm color code"""
    Cyan3: int = 43
    """(43) Xterm color code"""
    DarkTurquoise: int = 44
    """(44) Xterm color code"""
    Turquoise2: int = 45
    """(45) Xterm color code"""
    Green1: int = 46
    """(46) Xterm color code"""
    SpringGreen2: int = 47
    """(47) Xterm color code"""
    SpringGreen1: int = 48
    """(48) Xterm color code"""
    MediumSpringGreen: int = 49
    """(49) Xterm color code"""
    Cyan2: int = 50
    """(50) Xterm color code"""
    Cyan1: int = 51
    """(51) Xterm color code"""
    DarkRed: int = 52
    """(52) Xterm color code"""
    DeepPink4: int = 53
    """(53) Xterm color code"""
    Purple4: int = 54
    """(54) Xterm color code"""
    Purple4: int = 55
    """(55) Xterm color code"""
    Purple3: int = 56
    """(56) Xterm color code"""
    BlueViolet: int = 57
    """(57) Xterm color code"""
    Orange4: int = 58
    """(58) Xterm color code"""
    Grey37: int = 59
    """(59) Xterm color code"""
    MediumPurple4: int = 60
    """(60) Xterm color code"""
    SlateBlue3: int = 61
    """(61) Xterm color code"""
    SlateBlue3: int = 62
    """(62) Xterm color code"""
    RoyalBlue1: int = 63
    """(63) Xterm color code"""
    Chartreuse4: int = 64
    """(64) Xterm color code"""
    DarkSeaGreen4: int = 65
    """(65) Xterm color code"""
    PaleTurquoise4: int = 66
    """(66) Xterm color code"""
    SteelBlue: int = 67
    """(67) Xterm color code"""
    SteelBlue3: int = 68
    """(68) Xterm color code"""
    CornflowerBlue: int = 69
    """(69) Xterm color code"""
    Chartreuse3: int = 70
    """(70) Xterm color code"""
    DarkSeaGreen4: int = 71
    """(71) Xterm color code"""
    CadetBlue: int = 72
    """(72) Xterm color code"""
    CadetBlue: int = 73
    """(73) Xterm color code"""
    SkyBlue3: int = 74
    """(74) Xterm color code"""
    SteelBlue1: int = 75
    """(75) Xterm color code"""
    Chartreuse3: int = 76
    """(76) Xterm color code"""
    PaleGreen3: int = 77
    """(77) Xterm color code"""
    SeaGreen3: int = 78
    """(78) Xterm color code"""
    Aquamarine3: int = 79
    """(79) Xterm color code"""
    MediumTurquoise: int = 80
    """(80) Xterm color code"""
    SteelBlue1: int = 81
    """(81) Xterm color code"""
    Chartreuse2: int = 82
    """(82) Xterm color code"""
    SeaGreen2: int = 83
    """(83) Xterm color code"""
    SeaGreen1: int = 84
    """(84) Xterm color code"""
    SeaGreen1: int = 85
    """(85) Xterm color code"""
    Aquamarine1: int = 86
    """(86) Xterm color code"""
    DarkSlateGray2: int = 87
    """(87) Xterm color code"""
    DarkRed: int = 88
    """(88) Xterm color code"""
    DeepPink4: int = 89
    """(89) Xterm color code"""
    DarkMagenta: int = 90
    """(90) Xterm color code"""
    DarkMagenta: int = 91
    """(91) Xterm color code"""
    DarkViolet: int = 92
    """(92) Xterm color code"""
    Purple: int = 93
    """(93) Xterm color code"""
    Orange4: int = 94
    """(94) Xterm color code"""
    LightPink4: int = 95
    """(95) Xterm color code"""
    Plum4: int = 96
    """(96) Xterm color code"""
    MediumPurple3: int = 97
    """(97) Xterm color code"""
    MediumPurple3: int = 98
    """(98) Xterm color code"""
    SlateBlue1: int = 99
    """(99) Xterm color code"""
    Yellow4: int = 100
    """(100) Xterm color code"""
    Wheat4: int = 101
    """(101) Xterm color code"""
    Grey53: int = 102
    """(102) Xterm color code"""
    LightSlateGrey: int = 103
    """(103) Xterm color code"""
    MediumPurple: int = 104
    """(104) Xterm color code"""
    LightSlateBlue: int = 105
    """(105) Xterm color code"""
    Yellow4: int = 106
    """(106) Xterm color code"""
    DarkOliveGreen3: int = 107
    """(107) Xterm color code"""
    DarkSeaGreen: int = 108
    """(108) Xterm color code"""
    LightSkyBlue3: int = 109
    """(109) Xterm color code"""
    LightSkyBlue3: int = 110
    """(110) Xterm color code"""
    SkyBlue2: int = 111
    """(111) Xterm color code"""
    Chartreuse2: int = 112
    """(112) Xterm color code"""
    DarkOliveGreen3: int = 113
    """(113) Xterm color code"""
    PaleGreen3: int = 114
    """(114) Xterm color code"""
    DarkSeaGreen3: int = 115
    """(115) Xterm color code"""
    DarkSlateGray3: int = 116
    """(116) Xterm color code"""
    SkyBlue1: int = 117
    """(117) Xterm color code"""
    Chartreuse1: int = 118
    """(118) Xterm color code"""
    LightGreen: int = 119
    """(119) Xterm color code"""
    LightGreen: int = 120
    """(120) Xterm color code"""
    PaleGreen1: int = 121
    """(121) Xterm color code"""
    Aquamarine1: int = 122
    """(122) Xterm color code"""
    DarkSlateGray1: int = 123
    """(123) Xterm color code"""
    Red3: int = 124
    """(124) Xterm color code"""
    DeepPink4: int = 125
    """(125) Xterm color code"""
    MediumVioletRed: int = 126
    """(126) Xterm color code"""
    Magenta3: int = 127
    """(127) Xterm color code"""
    DarkViolet: int = 128
    """(128) Xterm color code"""
    Purple: int = 129
    """(129) Xterm color code"""
    DarkOrange3: int = 130
    """(130) Xterm color code"""
    IndianRed: int = 131
    """(131) Xterm color code"""
    HotPink3: int = 132
    """(132) Xterm color code"""
    MediumOrchid3: int = 133
    """(133) Xterm color code"""
    MediumOrchid: int = 134
    """(134) Xterm color code"""
    MediumPurple2: int = 135
    """(135) Xterm color code"""
    DarkGoldenrod: int = 136
    """(136) Xterm color code"""
    LightSalmon3: int = 137
    """(137) Xterm color code"""
    RosyBrown: int = 138
    """(138) Xterm color code"""
    Grey63: int = 139
    """(139) Xterm color code"""
    MediumPurple2: int = 140
    """(140) Xterm color code"""
    MediumPurple1: int = 141
    """(141) Xterm color code"""
    Gold3: int = 142
    """(142) Xterm color code"""
    DarkKhaki: int = 143
    """(143) Xterm color code"""
    NavajoWhite3: int = 144
    """(144) Xterm color code"""
    Grey69: int = 145
    """(145) Xterm color code"""
    LightSteelBlue3: int = 146
    """(146) Xterm color code"""
    LightSteelBlue: int = 147
    """(147) Xterm color code"""
    Yellow3: int = 148
    """(148) Xterm color code"""
    DarkOliveGreen3: int = 149
    """(149) Xterm color code"""
    DarkSeaGreen3: int = 150
    """(150) Xterm color code"""
    DarkSeaGreen2: int = 151
    """(151) Xterm color code"""
    LightCyan3: int = 152
    """(152) Xterm color code"""
    LightSkyBlue1: int = 153
    """(153) Xterm color code"""
    GreenYellow: int = 154
    """(154) Xterm color code"""
    DarkOliveGreen2: int = 155
    """(155) Xterm color code"""
    PaleGreen1: int = 156
    """(156) Xterm color code"""
    DarkSeaGreen2: int = 157
    """(157) Xterm color code"""
    DarkSeaGreen1: int = 158
    """(158) Xterm color code"""
    PaleTurquoise1: int = 159
    """(159) Xterm color code"""
    Red3: int = 160
    """(160) Xterm color code"""
    DeepPink3: int = 161
    """(161) Xterm color code"""
    DeepPink3: int = 162
    """(162) Xterm color code"""
    Magenta3: int = 163
    """(163) Xterm color code"""
    Magenta3: int = 164
    """(164) Xterm color code"""
    Magenta2: int = 165
    """(165) Xterm color code"""
    DarkOrange3: int = 166
    """(166) Xterm color code"""
    IndianRed: int = 167
    """(167) Xterm color code"""
    HotPink3: int = 168
    """(168) Xterm color code"""
    HotPink2: int = 169
    """(169) Xterm color code"""
    Orchid: int = 170
    """(170) Xterm color code"""
    MediumOrchid1: int = 171
    """(171) Xterm color code"""
    Orange3: int = 172
    """(172) Xterm color code"""
    LightSalmon3: int = 173
    """(173) Xterm color code"""
    LightPink3: int = 174
    """(174) Xterm color code"""
    Pink3: int = 175
    """(175) Xterm color code"""
    Plum3: int = 176
    """(176) Xterm color code"""
    Violet: int = 177
    """(177) Xterm color code"""
    Gold3: int = 178
    """(178) Xterm color code"""
    LightGoldenrod3: int = 179
    """(179) Xterm color code"""
    Tan: int = 180
    """(180) Xterm color code"""
    MistyRose3: int = 181
    """(181) Xterm color code"""
    Thistle3: int = 182
    """(182) Xterm color code"""
    Plum2: int = 183
    """(183) Xterm color code"""
    Yellow3: int = 184
    """(184) Xterm color code"""
    Khaki3: int = 185
    """(185) Xterm color code"""
    LightGoldenrod2: int = 186
    """(186) Xterm color code"""
    LightYellow3: int = 187
    """(187) Xterm color code"""
    Grey84: int = 188
    """(188) Xterm color code"""
    LightSteelBlue1: int = 189
    """(189) Xterm color code"""
    Yellow2: int = 190
    """(190) Xterm color code"""
    DarkOliveGreen1: int = 191
    """(191) Xterm color code"""
    DarkOliveGreen1: int = 192
    """(192) Xterm color code"""
    DarkSeaGreen1: int = 193
    """(193) Xterm color code"""
    Honeydew2: int = 194
    """(194) Xterm color code"""
    LightCyan1: int = 195
    """(195) Xterm color code"""
    Red1: int = 196
    """(196) Xterm color code"""
    DeepPink2: int = 197
    """(197) Xterm color code"""
    DeepPink1: int = 198
    """(198) Xterm color code"""
    DeepPink1: int = 199
    """(199) Xterm color code"""
    Magenta2: int = 200
    """(200) Xterm color code"""
    Magenta1: int = 201
    """(201) Xterm color code"""
    OrangeRed1: int = 202
    """(202) Xterm color code"""
    IndianRed1: int = 203
    """(203) Xterm color code"""
    IndianRed1: int = 204
    """(204) Xterm color code"""
    HotPink: int = 205
    """(205) Xterm color code"""
    HotPink: int = 206
    """(206) Xterm color code"""
    MediumOrchid1: int = 207
    """(207) Xterm color code"""
    DarkOrange: int = 208
    """(208) Xterm color code"""
    Salmon1: int = 209
    """(209) Xterm color code"""
    LightCoral: int = 210
    """(210) Xterm color code"""
    PaleVioletRed1: int = 211
    """(211) Xterm color code"""
    Orchid2: int = 212
    """(212) Xterm color code"""
    Orchid1: int = 213
    """(213) Xterm color code"""
    Orange1: int = 214
    """(214) Xterm color code"""
    SandyBrown: int = 215
    """(215) Xterm color code"""
    LightSalmon1: int = 216
    """(216) Xterm color code"""
    LightPink1: int = 217
    """(217) Xterm color code"""
    Pink1: int = 218
    """(218) Xterm color code"""
    Plum1: int = 219
    """(219) Xterm color code"""
    Gold1: int = 220
    """(220) Xterm color code"""
    LightGoldenrod2: int = 221
    """(221) Xterm color code"""
    LightGoldenrod2: int = 222
    """(222) Xterm color code"""
    NavajoWhite1: int = 223
    """(223) Xterm color code"""
    MistyRose1: int = 224
    """(224) Xterm color code"""
    Thistle1: int = 225
    """(225) Xterm color code"""
    Yellow1: int = 226
    """(226) Xterm color code"""
    LightGoldenrod1: int = 227
    """(227) Xterm color code"""
    Khaki1: int = 228
    """(228) Xterm color code"""
    Wheat1: int = 229
    """(229) Xterm color code"""
    Cornsilk1: int = 230
    """(230) Xterm color code"""
    Grey100: int = 231
    """(231) Xterm color code"""
    Grey3: int = 232
    """(232) Xterm color code"""
    Grey7: int = 233
    """(233) Xterm color code"""
    Grey11: int = 234
    """(234) Xterm color code"""
    Grey15: int = 235
    """(235) Xterm color code"""
    Grey19: int = 236
    """(236) Xterm color code"""
    Grey23: int = 237
    """(237) Xterm color code"""
    Grey27: int = 238
    """(238) Xterm color code"""
    Grey30: int = 239
    """(239) Xterm color code"""
    Grey35: int = 240
    """(240) Xterm color code"""
    Grey39: int = 241
    """(241) Xterm color code"""
    Grey42: int = 242
    """(242) Xterm color code"""
    Grey46: int = 243
    """(243) Xterm color code"""
    Grey50: int = 244
    """(244) Xterm color code"""
    Grey54: int = 245
    """(245) Xterm color code"""
    Grey58: int = 246
    """(246) Xterm color code"""
    Grey62: int = 247
    """(247) Xterm color code"""
    Grey66: int = 248
    """(248) Xterm color code"""
    Grey70: int = 249
    """(249) Xterm color code"""
    Grey74: int = 250
    """(250) Xterm color code"""
    Grey78: int = 251
    """(251) Xterm color code"""
    Grey82: int = 252
    """(252) Xterm color code"""
    Grey85: int = 253
    """(253) Xterm color code"""
    Grey89: int = 254
    """(254) Xterm color code"""
    Grey93: int = 255
    """(255) Xterm color code"""
