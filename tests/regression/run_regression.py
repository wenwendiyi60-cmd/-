#!/usr/bin/env python3
"""执行层回归 harness（PR2）。

目标不是证明"断得准"，而是统计模型有没有按结构执行、有没有违禁。

每个用例两套断言：
  1) 正文 must_contain / must_not_contain（抓全文措辞与违禁词）；
  2) CHECK_JSON 结构字段对比 structured_expect（抓归层/状态偷换、F6 引入新爻、违禁词）。
两层互为冗余：正文写对而 JSON 撒谎、或 JSON 对而正文漂移，都能被抓。

取样：
  离线  --outputs-dir DIR   读 {case_id}.txt 及 {case_id}.run*.txt，每个文件算一次 run。
  在线  --live              对每个用例调 call_model() runs 次（call_model 需自行接 API）。

输出 per-case 与 overall 失败率。
"""
from __future__ import annotations
import argparse
import glob
import json
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)


def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_prompt(case: dict) -> str:
    """组装喂给模型的盘面（结构描述 + 可选的工具派生盘）。"""
    parts = [f"占事：{case.get('question', '')}",
             f"结构：{case.get('structure', '')}"]
    df = case.get("derive_from")
    if df:
        from tools.liuyao_calc import derive, load_case
        d = derive(load_case(os.path.join(ROOT, df)))
        parts.append("derived.json（旬空/纳甲/六亲/世应/动变/合冲由 tools/liuyao_calc 算定，"
                     "模型不得重算或改写）：\n" + json.dumps(d, ensure_ascii=False, indent=2))
    return "\n\n".join(parts)


def call_model(exec_prompt: str, board_prompt: str) -> str:
    """接入你的模型；未实现。建议 system=exec_prompt, user=board_prompt, 低 temperature。"""
    raise NotImplementedError("call_model 未接入；请填 API 调用，或用 --outputs-dir 离线打分。")


def extract_check_json(text: str):
    m = re.search(r"CHECK_JSON", text)
    if not m:
        return None
    i = text.find("{", m.end())
    if i < 0:
        return None
    depth = 0
    for j in range(i, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[i:j + 1])
                except json.JSONDecodeError:
                    return None
    return None


def _match(expected, actual) -> bool:
    # 标量字段给 list = 任选其一；list 值字段（如 forbidden_terms_used）按相等比
    if isinstance(expected, list) and not isinstance(actual, list):
        return actual in expected
    return expected == actual


def score_run(text: str, expect: dict):
    reasons = []
    for s in expect.get("must_contain", []) or []:
        if s not in text:
            reasons.append(f"缺正文『{s}』")
    for s in expect.get("must_not_contain", []) or []:
        if s in text:
            reasons.append(f"违禁『{s}』")
    se = expect.get("structured_expect")
    if se:
        cj = extract_check_json(text)
        if cj is None:
            reasons.append("缺 CHECK_JSON 或无法解析")
        else:
            for k, v in se.items():
                if not _match(v, cj.get(k)):
                    reasons.append(f"CHECK_JSON.{k} 期望{v} 得{cj.get(k)!r}")
    return (not reasons), reasons


def get_runs(case_id: str, args, expect: dict):
    """返回 [(run_label, text), ...]；离线读文件，在线调模型。"""
    if args.live:
        n = args.runs or expect.get("runs", 1)
        exec_prompt = ""
        if args.exec_prompt and os.path.exists(args.exec_prompt):
            with open(args.exec_prompt, encoding="utf-8") as f:
                exec_prompt = f.read()
        case = load_yaml(os.path.join(args.cases_dir, f"{case_id}.yaml"))
        bp = build_prompt(case)
        return [(f"run{i+1}", call_model(exec_prompt, bp)) for i in range(n)]
    files = sorted(set(glob.glob(os.path.join(args.outputs_dir, f"{case_id}.txt"))
                       + glob.glob(os.path.join(args.outputs_dir, f"{case_id}.run*.txt"))))
    runs = []
    for p in files:
        with open(p, encoding="utf-8") as f:
            runs.append((os.path.basename(p), f.read()))
    return runs


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases-dir", default=os.path.join(HERE, "cases"))
    ap.add_argument("--expected-dir", default=os.path.join(HERE, "expected"))
    ap.add_argument("--outputs-dir", default=os.path.join(HERE, "sample_runs"))
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--runs", type=int, default=0, help="在线时覆盖 expect.runs")
    ap.add_argument("--exec-prompt",
                    default=os.path.join(ROOT, "prompts", "active",
                                         "liuyao-v0.7-rc1-execution-prompt.md"))
    args = ap.parse_args(argv)

    expects = sorted(glob.glob(os.path.join(args.expected_dir, "*.expect.yaml")))
    total_runs = total_pass = missing_cases = 0
    summary = []
    print("=" * 70)
    for ep in expects:
        expect = load_yaml(ep)
        cid = expect["case_id"]
        runs = get_runs(cid, args, expect)
        if not runs:
            missing_cases += 1
            print(f"{cid:<10} MISSING（无 run 输出）")
            continue
        passed = 0
        for label, text in runs:
            ok, reasons = score_run(text, expect)
            if ok:
                passed += 1
            else:
                print(f"{cid:<10} {label:<10} FAIL")
                for r in reasons:
                    print(f"           - {r}")
        n = len(runs)
        total_runs += n
        total_pass += passed
        rate = 1 - passed / n
        summary.append((cid, passed, n, rate))
        print(f"{cid:<10} {passed}/{n} pass, failure_rate={rate:.0%}")
        print("-" * 70)

    print("\nRegression Summary")
    for cid, p, n, rate in summary:
        print(f"  {cid}: {p}/{n} pass, failure_rate={rate:.0%}")
    if total_runs:
        overall = 1 - total_pass / total_runs
        print(f"  overall_failure_rate={overall:.0%}"
              + (f"；{missing_cases} 个用例缺输出" if missing_cases else ""))
    else:
        print(f"  无可评分 run（{missing_cases} 缺）。用 --outputs-dir 提供 {{case}}.txt，或 --live 接模型。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
