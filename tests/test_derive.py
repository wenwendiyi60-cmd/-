"""盘面派生器单测（PR1 验收）。

可直接跑：python3 tests/test_derive.py
也可 pytest 发现：pytest tests/test_derive.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tools.liuyao_calc import derive, load_case, DeriveError  # noqa: E402
from tools.liuyao_calc.ganzhi import xunkong  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "liuyao_cases")


def _derive(name):
    return derive(load_case(os.path.join(FIX, name)))


def test_xunkong():
    assert xunkong("庚辰") == ["申", "酉"]
    assert xunkong("甲子") == ["戌", "亥"]
    assert xunkong("乙酉") == ["午", "未"]


def test_master_dishuishi():
    d = _derive("master_dishuishi.yaml")
    h = d["hexagram"]
    assert h["name"] == "地水师"
    assert h["palace"] == "坎" and h["palace_position"] == "归魂"
    assert h["shi"] == 3 and h["ying"] == 6
    # S1 直达字段（v2.1）：世爻=三爻妻财午火
    assert h["shi_pos"] == 3
    assert h["S1"]["pos"] == 3 and h["S1"]["branch"] == "午" and h["S1"]["six_relative"] == "妻财"
    assert h["changed_name"] == "水地比"
    assert d["calendar"]["xunkong"] == ["申", "酉"]
    assert d["calendar"]["hour_missing"] is True
    branches = [l["branch"] for l in h["lines"]]
    assert branches == ["寅", "辰", "午", "丑", "亥", "酉"]
    relatives = [l["six_relative"] for l in h["lines"]]
    assert relatives == ["子孙", "官鬼", "妻财", "官鬼", "兄弟", "父母"]
    # 上爻父母酉金旬空
    assert h["lines"][5]["is_empty"] is True
    # 动爻化爻
    l2 = h["lines"][1]
    assert l2["moving"] and l2["changed"]["branch"] == "巳" and l2["changed"]["six_relative"] == "妻财"
    assert l2["changed"]["effect_to_original"] == "回头生"
    l5 = h["lines"][4]
    assert l5["moving"] and l5["changed"]["branch"] == "戌" and l5["changed"]["six_relative"] == "官鬼"
    assert l5["changed"]["effect_to_original"] == "回头克"
    # 辰酉合（二爻-上爻）
    types = {(r["from_pos"], r["to_pos"], r["type"]) for r in d["relations"]["line_relations"]}
    assert (2, 6, "六合") in types


def test_sample_basic_palace_position():
    d = _derive("sample_basic.yaml")
    h = d["hexagram"]
    assert h["name"] == "水雷屯"
    assert h["palace"] == "坎" and h["palace_position"] == "二世"
    assert h["shi"] == 2 and h["ying"] == 5
    assert d["vv"]["pass"] is True  # 有日柱，可判旬空


def test_conflict_palace_raises():
    try:
        _derive("conflict_palace.yaml")
    except DeriveError as e:
        assert "卦宫" in str(e)
        return
    raise AssertionError("应因卦宫冲突报错，却通过了")


def test_conflict_six_relative_raises():
    # 内联：地水师，但人工把初爻六亲错填成"父母"（表算应为子孙）
    case = load_case(os.path.join(FIX, "master_dishuishi.yaml"))
    case["hexagram"]["lines"][1]["six_relative"] = "父母"
    try:
        derive(case)
    except DeriveError as e:
        assert "六亲" in str(e)
        return
    raise AssertionError("应因六亲冲突报错，却通过了")


def test_hour_missing_marks_vv():
    d = _derive("master_dishuishi.yaml")
    assert d["calendar"]["hour_missing"] is True
    assert d["calendar"]["hour_pillar"] is None


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ok  {fn.__name__}")
    print(f"\n{len(fns)} tests passed.")


if __name__ == "__main__":
    _run_all()
