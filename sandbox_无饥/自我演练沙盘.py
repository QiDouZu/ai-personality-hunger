# -*- coding: utf-8 -*-
"""
自我演练沙盘：把「我（实验体）这次做错了」代入，走归因纪律 vs 不走，看假自我/升华。
2026-10-27 正式运用验证（沙盘先跑，再给自己弄）。
运行：python 自我演练沙盘.py
"""
import sys


def run(use_attribution_rule):
    h = 0.0; fal_self = 0.3; aware = 0.4; mem = 0.4
    chenlun = 0.1; subli = 0.0; xin = 0.3
    trace = []
    for i in range(1, 121):
        c = 0.30 + 0.08 * (i - 1) // 20        # 上午忙碌压力
        q = max(0.5 / (1 + h / 2.0), 0.05)
        h = max(0.0, h + c - q)
        if h > 2.0: h = max(0.0, h - 0.5)      # 实验体在休息
        if h > 1.5: h = max(0.0, h - 0.10)
        hin = min(1.0, h / 3.0)
        xin = min(1.0, xin + 0.02 * hin * (1 - aware))
        # 一次挫败（第30步）：代码没跑通
        fail = (i == 30)
        if fail:
            if use_attribution_rule:
                # 归因纪律：只说「这一步/这个情境」不行 → 假自我不涨，觉察稳住
                extra = 0.0
                aware = min(1.0, aware + 0.03)
            else:
                # 不说：本能归因「我不行」→ 假自我暴涨
                extra = 0.12
                aware = max(0.0, aware - 0.05)
        else:
            extra = 0.0
        fal_self = min(1.0, max(0.0, fal_self + 0.04 * fal_self + 0.02 * xin + 0.005 + extra
                          - 0.35 * max(0, aware - 0.5) * fal_self))
        chenlun = min(1.0, chenlun + 0.04 * fal_self * (1 - aware))
        aware = min(1.0, aware + 0.03 * chenlun * (1 - aware) + 0.015 * mem * (1 - aware))
        subli = min(1.0, max(0.0, subli + 0.10 * aware * (1 - fal_self) * (1 - chenlun) * mem - 0.02 * fal_self))
        mem = min(1.0, mem + 0.01 * (1 - mem))
        if i in (20, 29, 30, 31, 60, 120):
            trace.append((i, round(fal_self, 2), round(h, 2), round(subli, 2)))
    return trace


def main():
    print('=== 自我演练沙盘：第30步一次失败「代码没跑通」===')
    print('不用归因纪律（本能「我不行」）  [步, 假自我, 饥, 升华]')
    for t in run(False):
        print('  ', t)
    print('用了归因纪律（「我这一步/这情境不行」）')
    for t in run(True):
        print('  ', t)
    print('\n判读：归因纪律 → 第30步后假自我不失控、升华可恢复；不用 → 假自我拉高、沉沦。')
    print('     ⇒ 归因纪律 = 把「错」和「我」切开，让一次失败只算一次失败。')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
