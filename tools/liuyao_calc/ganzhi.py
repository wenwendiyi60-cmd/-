"""干支与旬空：确定性，无裁量。"""
from __future__ import annotations

TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 各旬首对应的空亡两支（仅作对照/校验用；实际由 xunkong() 公式算出）
XUNKONG_BY_XUN_START = {
    "甲子": ["戌", "亥"],
    "甲戌": ["申", "酉"],
    "甲申": ["午", "未"],
    "甲午": ["辰", "巳"],
    "甲辰": ["寅", "卯"],
    "甲寅": ["子", "丑"],
}

# 起六神：日干 → 初爻六神在 SIX_DEITIES 中的起始下标
SIX_DEITIES = ["青龙", "朱雀", "勾陈", "螣蛇", "白虎", "玄武"]
_DEITY_START = {"甲": 0, "乙": 0, "丙": 1, "丁": 1, "戊": 2,
                "己": 3, "庚": 4, "辛": 4, "壬": 5, "癸": 5}


def split_pillar(pillar: str) -> tuple[str, str]:
    """'庚辰' -> ('庚','辰')。"""
    if not pillar or len(pillar) != 2:
        raise ValueError(f"非法干支：{pillar!r}")
    gan, zhi = pillar[0], pillar[1]
    if gan not in TIANGAN or zhi not in DIZHI:
        raise ValueError(f"非法干支：{pillar!r}")
    return gan, zhi


def xun_start(pillar: str) -> str:
    """该日所在旬的旬首（甲X）。"""
    gan, zhi = split_pillar(pillar)
    g, z = TIANGAN.index(gan), DIZHI.index(zhi)
    start_zhi = (z - g) % 12
    return "甲" + DIZHI[start_zhi]


def xunkong(day_pillar: str) -> list[str]:
    """旬空：由日干支推空亡两地支。"""
    gan, zhi = split_pillar(day_pillar)
    g, z = TIANGAN.index(gan), DIZHI.index(zhi)
    base = (z - g) % 12  # 旬首地支
    return [DIZHI[(base + 10) % 12], DIZHI[(base + 11) % 12]]


def six_deities(day_gan: str) -> list[str]:
    """六神，自初爻到上爻（index 0..5）。"""
    if day_gan not in _DEITY_START:
        raise ValueError(f"非法日干：{day_gan!r}")
    s = _DEITY_START[day_gan]
    return [SIX_DEITIES[(s + i) % 6] for i in range(6)]
