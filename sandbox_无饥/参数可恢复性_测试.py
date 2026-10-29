# -*- coding: utf-8 -*-
"""参数可恢复性_测试.py —— 能不能从数据反推出参数？（防参数简并）（2026-10-27）

材料建议：用已知参数生成数据 → 拟合 → 看能否恢复。
  · 恢复 ≈ 生成值 → 参数可恢复（打中的是机制，不是参数巧合）
  · 恢复 ≠ 生成值（多个参数组合给同样读数）→ 参数简并，打中的是参数

测试：sigmoid 门槛模型，参数 = (r_c 门槛位置, tau 拐点宽度)
  生成：r_c=0.55, tau=0.08，+噪声
  拟合：网格搜索 (r_c, tau) 最小二乘
"""
import math
import random

random.seed(181)
TRUE_RC = 0.55
TRUE_TAU = 0.08
RS = [round(i * 0.05, 2) for i in range(21)]


def sigmoid(r, rc, tau):
    return 1 / (1 + math.exp(-(r - rc) / tau))


# 生成数据
data = []
for r in RS:
    v = sigmoid(r, TRUE_RC, TRUE_TAU) + random.uniform(-0.03, 0.03)
    data.append((r, max(0.0, min(1.0, v))))


def sse(rc, tau):
    return sum((sigmoid(r, rc, tau) - y) ** 2 for r, y in data)


def main():
    best = None
    for rc in [round(0.30 + i * 0.01, 2) for i in range(51)]:      # 0.30-0.80
        for tau in [round(0.02 + i * 0.01, 2) for i in range(22)]:  # 0.02-0.23
            s = sse(rc, tau)
            if best is None or s < best[0]:
                best = (s, rc, tau)
    s, rc, tau = best
    print('=' * 56)
    print(' 参数可恢复性测试（防参数简并）')
    print('=' * 56)
    print(f'生成参数：r_c={TRUE_RC} tau={TRUE_TAU}')
    print(f'拟合参数：r_c={rc} tau={tau}   (SSE={s:.5f})')
    print()
    print(f'恢复误差：r_c {abs(rc-TRUE_RC):.3f} / tau {abs(tau-TRUE_TAU):.3f}')
    print('判据：', '可恢复（打中机制）' if abs(rc - TRUE_RC) <= 0.03 and abs(tau - TRUE_TAU) <= 0.03
          else '参数简并（打中参数）')


if __name__ == '__main__':
    main()
