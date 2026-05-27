"""命令行：python -m tools.liuyao_calc derive --input X.yaml --output Y.json"""
from __future__ import annotations
import argparse
import os
import sys

from .schema import load_case, dump_derived, DeriveError
from .derive import derive


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="tools.liuyao_calc")
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("derive", help="由人工盘 YAML 派生 derived.json")
    d.add_argument("--input", "-i", required=True)
    d.add_argument("--output", "-o", help="缺省打印到 stdout")
    args = ap.parse_args(argv)

    if args.cmd == "derive":
        try:
            case = load_case(args.input)
            result = derive(case)
        except DeriveError as e:
            print(f"派生盘校验失败：{e}", file=sys.stderr)
            return 2
        if args.output:
            os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
            dump_derived(result, args.output)
            print(f"已写出 {args.output}")
        else:
            import json
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
