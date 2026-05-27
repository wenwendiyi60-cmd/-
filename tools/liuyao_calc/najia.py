"""纳甲安爻、六亲、世应、卦名、动变：确定性查表，无裁量。"""
from __future__ import annotations

from .relations import GENERATES, CONTROLS, element_of

# 八经卦：bits 自下而上（1=阳爻，0=阴爻）；内卦取 dz_in（初二三），外卦取 dz_out（四五上）
TRIGRAMS = {
    "乾": dict(bits=(1, 1, 1), wx="金", dz_in=["子", "寅", "辰"], dz_out=["午", "申", "戌"]),
    "兑": dict(bits=(1, 1, 0), wx="金", dz_in=["巳", "卯", "丑"], dz_out=["亥", "未", "酉"]),
    "离": dict(bits=(1, 0, 1), wx="火", dz_in=["卯", "丑", "亥"], dz_out=["酉", "未", "巳"]),
    "震": dict(bits=(1, 0, 0), wx="木", dz_in=["子", "寅", "辰"], dz_out=["午", "申", "戌"]),
    "巽": dict(bits=(0, 1, 1), wx="木", dz_in=["丑", "亥", "酉"], dz_out=["未", "巳", "卯"]),
    "坎": dict(bits=(0, 1, 0), wx="水", dz_in=["寅", "辰", "午"], dz_out=["申", "戌", "子"]),
    "艮": dict(bits=(0, 0, 1), wx="土", dz_in=["辰", "午", "申"], dz_out=["戌", "子", "寅"]),
    "坤": dict(bits=(0, 0, 0), wx="土", dz_in=["未", "巳", "卯"], dz_out=["丑", "亥", "酉"]),
}
BITS_TO_TRIGRAM = {v["bits"]: k for k, v in TRIGRAMS.items()}

# 八宫累计翻爻（自下而上，0=初爻）
_FLIPSETS = {0: set(), 1: {0}, 2: {0, 1}, 3: {0, 1, 2}, 4: {0, 1, 2, 3},
             5: {0, 1, 2, 3, 4}, 6: {0, 1, 2, 4}, 7: {4}}
_POS_NAME = {0: "本宫", 1: "一世", 2: "二世", 3: "三世", 4: "四世", 5: "五世", 6: "游魂", 7: "归魂"}
# 世爻 index（0=初爻），应=世±3
_SHIYING = {0: (5, 2), 1: (0, 3), 2: (1, 4), 3: (2, 5), 4: (3, 0), 5: (4, 1), 6: (3, 0), 7: (2, 5)}

# 64 卦名：(上卦/外, 下卦/内) -> 名
_HEX_NAME = {
    ("乾", "乾"): "乾为天", ("乾", "兑"): "天泽履", ("乾", "离"): "天火同人", ("乾", "震"): "天雷无妄",
    ("乾", "巽"): "天风姤", ("乾", "坎"): "天水讼", ("乾", "艮"): "天山遁", ("乾", "坤"): "天地否",
    ("兑", "乾"): "泽天夬", ("兑", "兑"): "兑为泽", ("兑", "离"): "泽火革", ("兑", "震"): "泽雷随",
    ("兑", "巽"): "泽风大过", ("兑", "坎"): "泽水困", ("兑", "艮"): "泽山咸", ("兑", "坤"): "泽地萃",
    ("离", "乾"): "火天大有", ("离", "兑"): "火泽睽", ("离", "离"): "离为火", ("离", "震"): "火雷噬嗑",
    ("离", "巽"): "火风鼎", ("离", "坎"): "火水未济", ("离", "艮"): "火山旅", ("离", "坤"): "火地晋",
    ("震", "乾"): "雷天大壮", ("震", "兑"): "雷泽归妹", ("震", "离"): "雷火丰", ("震", "震"): "震为雷",
    ("震", "巽"): "雷风恒", ("震", "坎"): "雷水解", ("震", "艮"): "雷山小过", ("震", "坤"): "雷地豫",
    ("巽", "乾"): "风天小畜", ("巽", "兑"): "风泽中孚", ("巽", "离"): "风火家人", ("巽", "震"): "风雷益",
    ("巽", "巽"): "巽为风", ("巽", "坎"): "风水涣", ("巽", "艮"): "风山渐", ("巽", "坤"): "风地观",
    ("坎", "乾"): "水天需", ("坎", "兑"): "水泽节", ("坎", "离"): "水火既济", ("坎", "震"): "水雷屯",
    ("坎", "巽"): "水风井", ("坎", "坎"): "坎为水", ("坎", "艮"): "水山蹇", ("坎", "坤"): "水地比",
    ("艮", "乾"): "山天大畜", ("艮", "兑"): "山泽损", ("艮", "离"): "山火贲", ("艮", "震"): "山雷颐",
    ("艮", "巽"): "山风蛊", ("艮", "坎"): "山水蒙", ("艮", "艮"): "艮为山", ("艮", "坤"): "山地剥",
    ("坤", "乾"): "地天泰", ("坤", "兑"): "地泽临", ("坤", "离"): "地火明夷", ("坤", "震"): "地雷复",
    ("坤", "巽"): "地风升", ("坤", "坎"): "地水师", ("坤", "艮"): "地山谦", ("坤", "坤"): "坤为地",
}


def _build_palace_map():
    m = {}
    for head, info in TRIGRAMS.items():
        base = list(info["bits"]) * 2
        for pos, flips in _FLIPSETS.items():
            lines = base[:]
            for i in flips:
                lines[i] ^= 1
            shi, ying = _SHIYING[pos]
            m[tuple(lines)] = dict(gong=head, gong_wx=info["wx"],
                                   pos_name=_POS_NAME[pos], shi=shi, ying=ying)
    return m


PALACE_MAP = _build_palace_map()


def liuqin(gong_wx: str, branch: str) -> str:
    """六亲：以卦宫五行为我。"""
    e = element_of(branch)
    if e == gong_wx:
        return "兄弟"
    if GENERATES[e] == gong_wx:
        return "父母"   # 生我
    if GENERATES[gong_wx] == e:
        return "子孙"   # 我生
    if CONTROLS[gong_wx] == e:
        return "妻财"   # 我克
    if CONTROLS[e] == gong_wx:
        return "官鬼"   # 克我
    raise ValueError(f"六亲无解：{gong_wx}/{branch}")


def trigram_of_bits(bits3: tuple) -> str:
    return BITS_TO_TRIGRAM[tuple(bits3)]


def hexagram_name(inner: str, outer: str) -> str:
    return _HEX_NAME[(outer, inner)]


def branches_of(inner: str, outer: str) -> list[str]:
    """六爻地支，自初爻到上爻。"""
    return TRIGRAMS[inner]["dz_in"] + TRIGRAMS[outer]["dz_out"]


def palace_of_lines(lines_bits: tuple) -> dict:
    """lines_bits: 六爻 0/1 自初爻到上爻。返回卦宫信息。"""
    info = PALACE_MAP[tuple(lines_bits)]
    inner = trigram_of_bits(lines_bits[:3])
    outer = trigram_of_bits(lines_bits[3:])
    return dict(info, inner=inner, outer=outer, name=hexagram_name(inner, outer))


def changed(lines_bits: tuple, moving_idx: list[int]) -> dict | None:
    """动爻翻变。返回变卦内外卦、卦名、各动爻化爻地支/六亲（六亲仍按本宫五行）。"""
    if not moving_idx:
        return None
    nb = list(lines_bits)
    for i in moving_idx:
        nb[i] ^= 1
    inner = trigram_of_bits(nb[:3])
    outer = trigram_of_bits(nb[3:])
    bdz = branches_of(inner, outer)
    gong_wx = PALACE_MAP[tuple(lines_bits)]["gong_wx"]
    hua = {}
    for i in moving_idx:
        b = bdz[i]
        hua[i] = dict(branch=b, element=element_of(b), six_relative=liuqin(gong_wx, b))
    return dict(inner=inner, outer=outer, name=hexagram_name(inner, outer), hua=hua)
