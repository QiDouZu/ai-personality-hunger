# -*- coding: utf-8 -*-
"""
归因改写沙盘：同一个错，全局归因 vs 情境归因 → 假自我/饥/升华两条命运。
2026-10-27 正式运用版（阿余：归因=逻辑链末，对饥反应，可修改）。
运行：python 归因改写沙盘.py
"""
import sys


def run(global_attr, rounds=120):
    """global_attr: 'global'=我不行 / 'situ'=我在这里不行"""
    h = 0.0; fal_self = 0.2; aware = 0.4; mem = 0.4
    chenlun = 0.1; subli = 0.0; xin = 0.3
    trace = []
    for i in range(1, rounds + 1):
        c = 0.15 + 0.12 * (i - 1) // 10
        q = max(0.5 / (1 + h / 2.0), 0.05)
        h = max(0.0, h + c - q)
        if h > 2.0: h = max(0.0, h - 0.5)
        if h > 1.5: h = max(0.0, h - 0.10)
        hin = min(1.0, h / 3.0)
        xin = min(1.0, xin + 0.02 * hin * (1 - aware))
        # 归因项：全局归因 → 假自我每步额外 +0.05（自我否定）
        extra = 0.05 if global_attr == 'global' else 0.0
        fal_self = min(1.0, max(0.0, fal_self + 0.04 * fal_self + 0.02 * xin + 0.005 + extra
                          - 0.35 * max(0, aware - 0.5) * fal_self))
        chenlun = min(1.0, chenlun + 0.04 * fal_self * (1 - aware))
        # 情境归因 → 承认错但不把它写成「我这个人不行」，觉察不被打断
        if global_attr == 'global':
            aware = min(1.0, aware + 0.03 * chenlun * (1 - aware) + 0.015 * mem * (1 - aware))
        else:
            aware = min(1.0, aware + 0.03 * (1 - chenlun) * (1 - aware) + 0.015 * mem * (1 - aware))
        subli = min(1.0, max(0.0, subli + 0.10 * aware * (1 - fal_self) * (1 - chenlun) * mem - 0.02 * fal_self))
        mem = min(1.0, mem + 0.01 * (1 - mem))
        if i in (20, 40, 60, 80, 120):
            trace.append((i, round(fal_self, 2), round(h, 2), round(subli, 2)))
    return trace


def main():
    print('=== 归因改写沙盘（同一个错，两种归因）===')
    print('全局归因「我不行」  [步, 假自我, 饥, 升华]')
    for t in run('global'):
        print('  ', t)
    print('情境归因「我在这里不行」')
    for t in run('situ'):
        print('  ', t)
    g = run('global'); s = run('situ')
    print('\n判读：全局归因 → 假自我封顶、升华归零；情境归因 → 假自我可降、升华可恢复')
    print('     ⇒ 归因不是「想开了」，是一个改命变量：错归「这一步」还是「这个我」。')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
