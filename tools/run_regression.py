#!/usr/bin/env python3
"""六爻执行口令回归跑批打分骨架。

把 T1-T3 + 母盘从"肉眼看"变成"可数的失败率"。对应执行层降错的"杠杆 4"。

LLM 执行是概率性的：一条规则跑通一次不代表稳定。用 --runs N 多跑几次，
按用例报命中率，再出整体失败率。

两种取样模式：
  --outputs-dir DIR   读 {id}.txt 作为模型输出（先把模型回复粘进文件，离线打分）
  --live              调用 call_model()（默认未接，需自行填 API；见函数内说明）

用法示例：
  python3 tools/run_regression.py --outputs-dir tests/sample_outputs
  python3 tools/run_regression.py --live --runs 5
"""
from __future__ import annotations
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)


def load_cases(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)['cases']


def build_prompt(case):
    """把用例输入 + 已校验排盘拼成喂给模型的盘面（演示杠杆 2）。"""
    parts = [f"占事/结构：{case['input']}"]
    pp = case.get('paipan')
    if pp:
        try:
            import liuyao_paipan as lp
            board = lp.render(lp.paipan(pp['inner'], pp['outer'], pp['month'],
                                        pp['day'], pp.get('moving')))
            parts.append("已校验排盘（旬空/纳甲/六亲/世应/旺衰/合冲由 tools/liuyao_paipan.py 算定，禁脑补改盘）：\n" + board)
        except Exception as e:  # noqa: BLE001
            parts.append(f"[排盘失败：{e}]")
    return "\n\n".join(parts)


def call_model(execution_prompt, board_prompt):
    """接入你的模型。未实现——按需填入 OpenAI / Anthropic 调用。

    需返回模型对该盘走完 F0-F7 的完整文本输出。建议：
      - system = execution_prompt（执行口令全文）
      - user   = board_prompt（build_prompt 的结果）
      - 低 temperature，强模型。
    """
    raise NotImplementedError(
        "call_model 未接入。请在此填入 API 调用，或改用 --outputs-dir 离线打分。")


def score(output, case):
    """返回 (passed, reasons)。"""
    reasons = []
    ok = True
    text = output or ""
    for s in case.get('expect_contains', []):
        if s not in text:
            ok = False
            reasons.append(f"缺『{s}』")
    for group in case.get('expect_any', []):
        if not any(s in text for s in group):
            ok = False
            reasons.append("缺 任一(" + "/".join(group) + ")")
    for s in case.get('expect_absent', []):
        if s in text:
            ok = False
            reasons.append(f"违禁『{s}』")
    return ok, reasons


def get_output(case, args, run_idx):
    if args.outputs_dir:
        path = os.path.join(args.outputs_dir, f"{case['id']}.txt")
        if not os.path.exists(path):
            return None
        with open(path, encoding='utf-8') as f:
            return f.read()
    if args.live:
        exec_prompt = ""
        if args.exec_prompt and os.path.exists(args.exec_prompt):
            with open(args.exec_prompt, encoding='utf-8') as f:
                exec_prompt = f.read()
        return call_model(exec_prompt, build_prompt(case))
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cases', default=os.path.join(ROOT, 'tests', 'regression_cases.json'))
    ap.add_argument('--outputs-dir', help='读 {id}.txt 作为模型输出')
    ap.add_argument('--live', action='store_true', help='调用 call_model()')
    ap.add_argument('--exec-prompt', default=os.path.join(
        ROOT, 'prompts', 'active', 'liuyao-v0.7-rc1-execution-prompt.md'))
    ap.add_argument('--runs', type=int, default=1, help='每用例跑几次（--live 抓概率性）')
    args = ap.parse_args()

    if not args.outputs_dir and not args.live:
        ap.error('需指定 --outputs-dir 或 --live')

    cases = load_cases(args.cases)
    total_runs = total_pass = missing = 0
    print(f"{'用例':<8} {'题型':<28} 命中率  结果")
    print('-' * 78)
    for case in cases:
        runs = args.runs
        passes = 0
        evaluated = 0
        last_reasons = []
        for r in range(runs):
            out = get_output(case, args, r)
            if out is None:
                missing += 1
                continue
            evaluated += 1
            ok, reasons = score(out, case)
            if ok:
                passes += 1
            else:
                last_reasons = reasons
        if evaluated == 0:
            print(f"{case['id']:<8} {case['题型']:<28}  --     MISSING(无输出)")
            continue
        total_runs += evaluated
        total_pass += passes
        rate = passes / evaluated
        tag = 'PASS' if passes == evaluated else ('FAIL' if passes == 0 else 'FLAKY')
        detail = '' if tag == 'PASS' else '  ' + '；'.join(last_reasons)
        print(f"{case['id']:<8} {case['题型']:<28} {passes}/{evaluated}   {tag}{detail}")

    print('-' * 78)
    if total_runs:
        fail_rate = 1 - total_pass / total_runs
        print(f"整体：{total_pass}/{total_runs} 通过，失败率 {fail_rate:.0%}"
              + (f"；{missing} 个用例缺输出" if missing else ""))
    else:
        print(f"无可评分输出（{missing} 缺）。用 --outputs-dir 提供 {{id}}.txt，或 --live 接模型。")
    return 0


if __name__ == '__main__':
    sys.exit(main())
