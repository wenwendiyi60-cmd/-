"""派生器：读人工盘 → 校验 → 补确定性字段 → 输出 derived 结构。

只做确定性派生（旬空/纳甲/六亲/世应/动变/五行/月日生克/六合六冲/空亡/VV）。
不做旺衰档、病药归层、安危外放、应期、用神选择——那些留给模型在 F3-F7 裁量。
人工已填的 name/palace/shi/ying/branch/six_relative/six_deity 与规则表冲突时直接报错。
"""
from __future__ import annotations

from . import najia, ganzhi
from .relations import (element_of, month_relation, day_relation,
                        changed_branch_effect, find_pairs, LIU_HE, LIU_CHONG)
from .schema import DeriveError, normalize_lines


def _bit(yin_yang: str) -> int:
    if yin_yang == "yang":
        return 1
    if yin_yang == "yin":
        return 0
    raise DeriveError(f"yin_yang 非法：{yin_yang!r}（应为 yin/yang）")


def _flip(yin_yang: str) -> str:
    return "yin" if yin_yang == "yang" else "yang"


def derive(case: dict) -> dict:
    conflicts: list[str] = []

    hexa = case.get("hexagram") or {}
    lines_in = normalize_lines(hexa.get("lines") or {})

    # 1) bits 自初爻到上爻
    bits = []
    for pos in range(1, 7):
        yy = lines_in[pos].get("yin_yang")
        if yy is None:
            raise DeriveError(f"第{pos}爻缺 yin_yang，盘面不可读")
        bits.append(_bit(yy))
    bits = tuple(bits)

    # 2) 卦宫 / 内外卦 / 卦名 / 世应（确定性）
    pinfo = najia.palace_of_lines(bits)
    gong_wx = pinfo["gong_wx"]
    comp_branches = najia.branches_of(pinfo["inner"], pinfo["outer"])
    comp_shi_pos = pinfo["shi"] + 1   # 转 1-based
    comp_ying_pos = pinfo["ying"] + 1

    # 3) 校验人工填的卦名 / 卦宫 / 世应
    if hexa.get("name") and hexa["name"] != pinfo["name"]:
        conflicts.append(f"卦名：人工={hexa['name']} 表算={pinfo['name']}")
    if hexa.get("palace") and hexa["palace"] != pinfo["gong"]:
        conflicts.append(f"卦宫：人工={hexa['palace']} 表算={pinfo['gong']}")
    sy = case.get("shi_ying") or {}
    if sy.get("shi") is not None and int(sy["shi"]) != comp_shi_pos:
        conflicts.append(f"世爻：人工={sy['shi']} 表算={comp_shi_pos}")
    if sy.get("ying") is not None and int(sy["ying"]) != comp_ying_pos:
        conflicts.append(f"应爻：人工={sy['ying']} 表算={comp_ying_pos}")

    # 4) 历法字段
    cal = case.get("calendar") or {}
    month_pillar = cal.get("month_pillar")
    day_pillar = cal.get("day_pillar")
    hour_pillar = cal.get("hour_pillar")
    month_branch = ganzhi.split_pillar(month_pillar)[1] if month_pillar else None
    day_gan = day_branch = None
    kong: list[str] = []
    deities = [None] * 6
    if day_pillar:
        day_gan, day_branch = ganzhi.split_pillar(day_pillar)
        kong = ganzhi.xunkong(day_pillar)
        deities = ganzhi.six_deities(day_gan)

    moving_idx = [i for i in range(6) if lines_in[i + 1].get("is_moving")]
    bian = najia.changed(bits, moving_idx)

    # 5) 逐爻校验 + 组装
    out_lines = []
    for i in range(6):
        pos = i + 1
        src = lines_in[pos]
        branch = comp_branches[i]
        el = element_of(branch)
        lq = najia.liuqin(gong_wx, branch)
        deity = deities[i]
        # 人工值校验
        if src.get("branch") and src["branch"] != branch:
            conflicts.append(f"第{pos}爻地支：人工={src['branch']} 表算={branch}")
        if src.get("six_relative") and src["six_relative"] != lq:
            conflicts.append(f"第{pos}爻六亲：人工={src['six_relative']} 表算={lq}")
        if src.get("six_deity") and deity and src["six_deity"] != deity:
            conflicts.append(f"第{pos}爻六神：人工={src['six_deity']} 表算={deity}")

        moving = bool(src.get("is_moving"))
        line = dict(
            pos=pos,
            yin_yang=src["yin_yang"],
            moving=moving,
            changed_yin_yang=_flip(src["yin_yang"]) if moving else src["yin_yang"],
            branch=branch,
            element=el,
            six_relative=lq,
            six_deity=deity,
            is_shi=(pos == comp_shi_pos),
            is_ying=(pos == comp_ying_pos),
            is_empty=(branch in kong),
            hidden=src.get("hidden"),
            month_relation=month_relation(branch, month_branch) if month_branch else None,
            day_relation=day_relation(branch, day_branch) if day_branch else None,
        )
        if moving and bian:
            hua = bian["hua"][i]
            line["changed"] = dict(
                branch=hua["branch"], element=hua["element"],
                six_relative=hua["six_relative"],
                effect_to_original=changed_branch_effect(branch, hua["branch"]),
            )
        out_lines.append(line)

    if conflicts:
        raise DeriveError("人工输入与规则表冲突：\n  - " + "\n  - ".join(conflicts))

    # 6) 爻间六合六冲
    pairs_src = [(ln["pos"], ln["branch"]) for ln in out_lines]
    he, chong = find_pairs(pairs_src)
    line_relations = (
        [dict(from_pos=a, to_pos=b, type="六合", from_branch=ba, to_branch=bb) for a, b, ba, bb in he]
        + [dict(from_pos=a, to_pos=b, type="六冲", from_branch=ba, to_branch=bb) for a, b, ba, bb in chong]
    )

    # 7) VV
    vv = dict(
        hexagram_readable=True,
        shi_ying_readable=True,
        moving_lines_readable=True,
        xunkong_readable=bool(day_pillar),
        pass_=bool(day_pillar),
    )

    return {
        "case_id": case.get("case_id"),
        "question": case.get("question"),
        "calendar": {
            "date": cal.get("date"),
            "month_pillar": month_pillar, "month_branch": month_branch,
            "day_pillar": day_pillar, "day_branch": day_branch,
            "hour_pillar": hour_pillar,
            "xunkong": kong or None,
            "hour_missing": hour_pillar is None,
        },
        "hexagram": {
            "name": pinfo["name"], "palace": pinfo["gong"], "palace_element": gong_wx,
            "palace_position": pinfo["pos_name"],
            "inner": pinfo["inner"], "outer": pinfo["outer"],
            "changed_name": bian["name"] if bian else None,
            "shi": comp_shi_pos, "ying": comp_ying_pos,
            "moving_positions": [i + 1 for i in moving_idx],
            "lines": out_lines,
        },
        "relations": {
            "liu_he_pairs": [list(p) for p in LIU_HE],
            "liu_chong_pairs": [list(p) for p in LIU_CHONG],
            "line_relations": line_relations,
        },
        "vv": {k.rstrip("_"): v for k, v in vv.items()},
        "_provenance": "tools/liuyao_calc — 确定性派生；模型不得改写本文件字段",
    }
