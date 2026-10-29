# -*- coding: utf-8 -*-
"""模拟人类_沙盘.py —— 人类版两步法：连续感知 → 先得一堆 → 筛一些（2026-10-27）

理论：人=连续流接收（感知适应：习惯后剩下不吸收）+ 主动筛选（挑谁进矛盾池）。
逻辑：每步都有一堆信号（连续感知），先全收（得到一堆），再主动筛（只挑值得的进矛盾池）。
对照：
  · 不筛：每步信号全进 → 矛盾库存高、抖动大、噪声混入
  · 筛：主动挑（只收与目标相关/反常的）→ 库存低而平、有效率高
判据：筛的人类库存低、抖动低、有效矛盾率高。
"""
import math
import random

random.seed(11)


def stream(steps=300):
    """连续信号流：每步一堆（目标相关 30%）。"""
    out = []
    for _ in range(steps):
        rel = random.random() < 0.3
        v = random.gauss(1.5, 0.4) if rel else random.gauss(0.8, 0.6)
        out.append((v, rel))
    return out


def run(sieve=True, s=None, v=0.5, adapt=0.03):
    B = 1.0
    trace, entered = [], []
    base = 1.0
    for val, rel in s:
        # 先得一堆：每步都收到（连续）
        if sieve:
            # 筛一些：只收与目标相关的（相关=值得要）
            take = rel
        else:
            take = True
        # 适应过滤：习惯后剩下不吸收（人脑的减）
        novel = max(0.0, val - adapt)
        if take and novel > 0:
            entered.append(rel)
            B = max(0.0, B * (1 - v) + novel)
        else:
            B = max(0.0, B * (1 - v))
        trace.append(round(B, 3))
    steady = trace[10:]
    mean = sum(steady) / len(steady) if steady else 0.0
    var = sum((b - mean) ** 2 for b in steady) / len(steady) if steady else 0.0
    eff = sum(1 for r in entered if r) / len(entered) if entered else 0.0
    return {'mean': round(mean, 3), 'std': round(math.sqrt(var), 3),
            'eff': round(eff, 3), 'n': len(entered)}


def main():
    s = stream()
    no = run(sieve=False, s=s)
    yes = run(sieve=True, s=s)
    print('=' * 66)
    print(' 模拟人类：连续感知 → 先得一堆 → 筛一些')
    print('=' * 66)
    print(f"{'':<8}{'进矛盾池':>9} {'库存均值':>9} {'库存抖动':>9} {'有效率':>8}")
    print(f"{'不筛':<8}{no['n']:>9} {no['mean']:>9} {no['std']:>9} {no['eff']:>8}")
    print(f"{'筛':<8}{yes['n']:>9} {yes['mean']:>9} {yes['std']:>9} {yes['eff']:>8}")
    print()
    print(' 判据：筛的库存更低：', '是' if yes['mean'] < no['mean'] else '否')
    print(' 判据：筛的抖动更低：', '是' if yes['std'] < no['std'] else '否')
    print(' 判据：筛的有效率更高：', '是' if yes['eff'] > no['eff'] else '否')
    print()
    print(' 结论：人每秒都收到一堆（连续感知），但先得一堆不是全进矛盾池——')
    print('       主动筛过再进，库存才平、有效才高。**筛=人版的获取方法。**')


if __name__ == '__main__':
    main()
