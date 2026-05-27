"""五行生克、六合六冲、月日关系：确定性，无裁量。

关系一律以"爻"为视角，取值五选一：
  生   = 参照(月/日)生爻      爻得生
  克   = 参照(月/日)克爻      爻受克
  泄   = 爻生参照            爻泄气
  耗   = 爻克参照            爻耗力
  比和 = 同五行              临/比和
"""
from __future__ import annotations

ELEMENT_OF_BRANCH = {
    "寅": "木", "卯": "木",
    "巳": "火", "午": "火",
    "申": "金", "酉": "金",
    "亥": "水", "子": "水",
    "辰": "土", "戌": "土", "丑": "土", "未": "土",
}

GENERATES = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
CONTROLS = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

LIU_HE = [("子", "丑"), ("寅", "亥"), ("卯", "戌"), ("辰", "酉"), ("巳", "申"), ("午", "未")]
LIU_CHONG = [("子", "午"), ("丑", "未"), ("寅", "申"), ("卯", "酉"), ("辰", "戌"), ("巳", "亥")]

_HE_SET = {frozenset(p) for p in LIU_HE}
_CHONG_SET = {frozenset(p) for p in LIU_CHONG}


def element_of(branch: str) -> str:
    return ELEMENT_OF_BRANCH[branch]


def is_he(a: str, b: str) -> bool:
    return frozenset((a, b)) in _HE_SET


def is_chong(a: str, b: str) -> bool:
    return frozenset((a, b)) in _CHONG_SET


def element_relation(line_el: str, ref_el: str) -> str:
    """ref(月/日)对爻的关系，以爻为视角。"""
    if line_el == ref_el:
        return "比和"
    if GENERATES[ref_el] == line_el:
        return "生"   # ref 生 爻
    if CONTROLS[ref_el] == line_el:
        return "克"   # ref 克 爻
    if GENERATES[line_el] == ref_el:
        return "泄"   # 爻 生 ref
    if CONTROLS[line_el] == ref_el:
        return "耗"   # 爻 克 ref
    raise ValueError(f"五行无解：{line_el} / {ref_el}")


def branch_relation(line_branch: str, ref_branch: str) -> str:
    return element_relation(element_of(line_branch), element_of(ref_branch))


def month_relation(line_branch: str, month_branch: str) -> dict:
    return {
        "relation": branch_relation(line_branch, month_branch),
        "is_month_break": is_chong(line_branch, month_branch),  # 月破：被月冲
    }


def day_relation(line_branch: str, day_branch: str) -> dict:
    return {
        "relation": branch_relation(line_branch, day_branch),
        "is_day_clash": is_chong(line_branch, day_branch),  # 日冲/暗动
    }


def changed_branch_effect(original_branch: str, changed_branch: str) -> str:
    """化爻对本爻：回头生 / 回头克 / 化进退（比和按进退另判，这里只给生克）/ 无。"""
    o, c = element_of(original_branch), element_of(changed_branch)
    if c == o:
        return "比和"
    if GENERATES[c] == o:
        return "回头生"
    if CONTROLS[c] == o:
        return "回头克"
    if GENERATES[o] == c:
        return "化泄"
    if CONTROLS[o] == c:
        return "化耗"
    return "无"


def find_pairs(branches: list[str]):
    """在一组(pos, branch)里找六合/六冲对。branches: list of (pos, branch)。"""
    he, chong = [], []
    n = len(branches)
    for i in range(n):
        for j in range(i + 1, n):
            pa, ba = branches[i]
            pb, bb = branches[j]
            if is_he(ba, bb):
                he.append((pa, pb, ba, bb))
            if is_chong(ba, bb):
                chong.append((pa, pb, ba, bb))
    return he, chong
