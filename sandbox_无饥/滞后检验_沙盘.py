# -*- coding: utf-8 -*-
"""滞后检验_沙盘.py —— 门槛是「相变」还是「饱和」？（2026-10-27）

来源：DeepSeek 网页材料（相对=验证流程）：
  「r≈0.55 的 sigmoid 拐点，如果只有 sigmoid 没有滞后/临界慢化，
    那它是平滑参数效应，不是相变；理解形式要从『分岔』弱化为『饱和点』。」

检验：r 从 0→1 正扫，再从 1→0 反扫。
  · 真相变（双稳态）→ 正扫和反扫的切换点不重合 = 迟滞环（hysteresis）
  · 平滑效应（无滞后）→ 正反扫切换点几乎重合

模型：状态 s（0=全收，1=筛选），
  p_s = sigmoid((r - r_c)/τ)   （r 越大越倾向筛选）
  s_{t+1} = s_t + α*(p_s - s_t)  （平滑跟随，有惰性）
  行为：s > 0.5 → 筛，否则全收
判据：|r_up - r_down| > 0.03 → 有滞后（相变）；否则 → 无滞后（饱和）
"""
import random

random.seed(171)
tau = 0.08
alpha = 0.12
r_c = 0.55


def one_r(r, n_steps=300, s0=0.0):
    s = s0
    p = 1 / (1 + __import__('math').exp(-(r - r_c) / tau))
    for _ in range(n_steps):
        s += alpha * (p - s) + random.uniform(-0.02, 0.02)  # 噪声
        s = max(0.0, min(1.0, s))
    return s


def main():
    rs = [round(i * 0.025, 3) for i in range(41)]  # 0.0 - 1.0
    # 正扫（从全收出发）
    up = []
    s_up = 0.0
    for r in rs:
        s_up = one_r(r, s0=s_up)
        up.append(s_up)
    # 反扫（从筛选出发）
    down = []
    s_down = 1.0
    for r in reversed(rs):
        s_down = one_r(r, s0=s_down)
        down.append(s_down)
    down = list(reversed(down))

    # 切换点（穿 0.5 的 r）
    def cross(vals, thr=0.5):
        for i in range(1, len(vals)):
            if (vals[i - 1] - thr) * (vals[i] - thr) <= 0:
                return rs[i]
        return None

    r_up = cross(up)
    r_down = cross(down)
    print('=' * 60)
    print(' 滞后检验：门槛是相变还是饱和？')
    print('=' * 60)
    print(f'{"r":>6}{"正扫s":>8}{"反扫s":>8}')
    for i in range(0, len(rs), 4):
        print(f'{rs[i]:>6.2f}{up[i]:>8.3f}{down[i]:>8.3f}')
    print()
    print(f'正扫切换点 r_up = {r_up}')
    print(f'反扫切换点 r_down = {r_down}')
    if r_up is not None and r_down is not None:
        gap = abs(r_up - r_down)
        print(f'迟滞环宽度 = {gap:.3f}')
        print('判据：', '有滞后（真相变/双稳态）' if gap > 0.03 else '无滞后（平滑饱和）')
    else:
        print('判据：未出现切换点（模型退化）')


if __name__ == '__main__':
    main()
