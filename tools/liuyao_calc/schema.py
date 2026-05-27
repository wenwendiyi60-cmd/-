"""输入读取 / 输出写出 / 错误类型。"""
from __future__ import annotations
import json
import yaml


class DeriveError(Exception):
    """派生盘校验失败：人工输入与规则表冲突，或盘面不可读。"""


def load_case(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def dump_derived(derived: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(derived, f, ensure_ascii=False, indent=2)
        f.write("\n")


def normalize_lines(raw: dict) -> dict:
    """把 YAML 的行 map（键可能是 int 或 str 的 1..6）规整为 {int: dict}。"""
    out = {}
    for k, v in raw.items():
        pos = int(k)
        if pos < 1 or pos > 6:
            raise DeriveError(f"爻位非法：{k!r}（应为 1..6）")
        out[pos] = v or {}
    if set(out) != {1, 2, 3, 4, 5, 6}:
        raise DeriveError(f"爻位不全：{sorted(out)}（需 1..6 各一）")
    return out
