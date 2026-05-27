"""六爻确定性盘面派生器。

把旬空、纳甲、六亲、世应、动变、五行、月日生克、六合六冲、空亡等确定性字段
从模型口算里拿走：读人工盘 YAML → 校验人工值 → 输出 derived.json。
模型只解释 derived.json，不再自己推盘。
"""
from .derive import derive
from .schema import load_case, dump_derived, DeriveError

__all__ = ["derive", "load_case", "dump_derived", "DeriveError"]
