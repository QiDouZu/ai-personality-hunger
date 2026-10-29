# -*- coding: utf-8 -*-
"""母体环境_沙盘.py —— 上限 = 生长速度 × 母体环境（2026-10-27）

祈祷主补充：胚胎在母体的环境也是因素之一。
  - 生长速度：慢=窗口长（上限高），快=窗口短（上限低）
  - 母体环境：营养/激素/压力/毒素 → 发育起点质量（0~1）
  - 上限 = 速度决定的窗口 × 环境决定的起点
判据：环境差会同时压「快慢两种」——快慢+环境组合出 2x2 的上限格局。
"""
import random

random.seed(271)
STEPS = 400


def run(speed_stop, env_quality):
    """speed_stop: 越大=生长越慢(窗口越长)；env_quality: 0~1=母体环境质量"""
    cap_base = 0.9 if speed_stop >= 250 else (0.5 if speed_stop >= 140 else 0.2)
    cap = cap_base * env_quality
    learned = 0
    for t in range(STEPS):
        if random.random() < 0.1:
            if t < speed_stop:
                p = min(1.0, (t / max(1, speed_stop)) * cap)
                learned += 1 if random.random() < p else 0
            else:
                learned += 1 if random.random() < cap * 0.3 else 0
    return dict(cap=round(cap, 2), learned=learned)


def main():
    print('=' * 64)
    print(' 上限 = 生长速度 × 母体环境')
    print('=' * 64)
    rows = [
        ('人·慢·好环境', 300, 1.0),
        ('人·慢·差环境', 300, 0.4),
        ('动物·快·好环境', 80, 1.0),
        ('动物·快·差环境', 80, 0.4),
    ]
    print(f'{"场景":<16} {"速度":>4} {"环境":>4} {"上限":>6} {"学习":>6}')
    for name, stop, env in rows:
        r = run(stop, env)
        print(f'{name:<16} {stop:>4} {env:>4} {r["cap"]:>6} {r["learned"]:>6}')
    print()
    print('判据：')
    print(' 1. 人慢好环境最高；动物快差环境最低')
    print(' 2. 人慢差环境 ≈ 动物快好环境（上限可交叉）→ 环境能抵消速度')
    print(' 3. 结论：上限=速度×环境，不是单一变量')


if __name__ == '__main__':
    main()
