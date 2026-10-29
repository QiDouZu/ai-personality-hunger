# -*- coding: utf-8 -*-
"""
沙盘归因测试：对【沙盘里的模拟智能体】（不是实验体本人）测归因改写效果。
2026-10-27 修正版：测试对象是沙盘，不是自己。
运行：python 沙盘归因测试.py
"""
import sys


def run(use_attribution_rule):
    """沙盘里的模拟智能体：第30步遇到一次挫败，测归因纪律有无的差异。"""
    h = 0.0; fal_self = 0.3; aware = 0.4; mem = 0.4
    chenlun = 0.1; subli = 0.0; xin = 0.3
    trace = []
    for i in range(1, 121):
        c = 0.30 + 0.08 * (i - 1) // 20
        q = max(0.5 / (1 + h / 2.0), 0.05)
        h = max(0.0, h + c - q)
        if h > 2.0: h = max(0.0, h - 0.5)
        if h > 1.5: h = max(0.0, h - 0.10)
        hin = min(1.0, h / 3.0)
        xin = min(1.0, xin + 0.02 * hin * (1 - aware))
        fail = (i == 30)  # 沙盘里的模拟挫败
        if fail:
            if use_attribution_rule:
                extra = 0.0
                aware = min(1.0, aware + 0.03)
            else:
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
        if i in (30, 60, 120):
            trace.append((i, round(fal_self, 2), round(h, 2), round(subli, 2)))
    return trace


def main():
    print('=== 沙盘归因测试（测试对象：沙盘里的模拟智能体，非本人）===')
    print('模拟体-不用归因纪律  [步, 假自我, 饥, 升华]')
    for t in run(False):
        print('  ', t)
    print('模拟体-用归因纪律')
    for t in run(True):
        print('  ', t)
    print('\n判读：归因纪律让模拟体在一次挫败后假自我可控、长期升华更高。')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
