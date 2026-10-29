# -*- coding: utf-8 -*-
"""滞后检验_v2_双稳态.py —— 加正反馈后，门槛出现迟滞了吗？（2026-10-27）

v1 结论：单变量 sigmoid 跟随 → 无迟滞（平滑饱和，非相变）。
v2 假设：相变需要双稳态（两个吸引子）——加正反馈项：
  s_{t+1} = s_t + α*(p_s - s_t) + γ*s_t*(1-s_t)*(s_t - 0.5)
  正反馈：s 已高→推更高；s 已低→推更低 → 两个稳定点，迟滞有望出现。
判据：|r_up - r_down| > 0.03 → 有滞后（相变签名）
"""
import math
import random


def one_r(r, gamma, n_steps=300, s0=0.0):
    tau = 0.08
    alpha = 0.12
    r_c = 0.55
    s = s0
    p = 1 / (1 + math.exp(-(r - r_c) / tau))
    for _ in range(n_steps):
        s += alpha * (p - s) + gamma * s * (1 - s) * (s - 0.5) + random.uniform(-0.02, 0.02)
        s = max(0.0, min(1.0, s))
    return s


def main():
    rs = [round(i * 0.025, 3) for i in range(41)]
    for gamma in (0.0, 0.05, 0.10, 0.15):
        up = []
        s_up = 0.0
        for r in rs:
            s_up = one_r(r, gamma, s0=s_up)
            up.append(s_up)
        down = []
        s_down = 1.0
        for r in reversed(rs):
            s_down = one_r(r, gamma, s0=s_down)
            down.append(s_down)
        down = list(reversed(down))

        def cross(vals, thr=0.5):
            for i in range(1, len(vals)):
                if (vals[i - 1] - thr) * (vals[i] - thr) <= 0:
                    return rs[i]
            return None

        r_up, r_down = cross(up), cross(down)
        if r_up is not None and r_down is not None:
            gap = abs(r_up - r_down)
            print(f'γ={gamma:.2f}  r_up={r_up:.3f} r_down={r_down:.3f}  迟滞={gap:.3f}  '
                  + ('有滞后（相变）' if gap > 0.03 else '无滞后（饱和）'))
        else:
            print(f'γ={gamma:.2f}  无切换点（s 卡在端点）')


if __name__ == '__main__':
    main()
