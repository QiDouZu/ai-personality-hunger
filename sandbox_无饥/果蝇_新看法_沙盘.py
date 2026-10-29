# -*- coding: utf-8 -*-
"""果蝇_新看法_沙盘.py —— 用「优先级调制」重测果蝇（2026-10-27）

新看法（理论共同点）：
  饥不是「驱动行为」，是「调优先级的场合设定子」——饥饿把「食物」设成当前的
  关注目标（优先级↑），果蝇按优先级选刺激；NPF=优先级调制器，不是驱动本身。

对照旧看法（NPF=直接驱动找食物：饥高→找食）。
测试：两种模型在 NPF 突变表型上谁解释得更好：
  · 旧看法：NPF 突变 → 找食驱动没了 → 完全不找
  · 新看法：NPF 突变 → 优先级调制失效 → 食物不再被设为目标 → 不主动找（但低优先级随机撞见仍会吃）
判据：新看法能同时解释「不找（高优先级缺）」+「偶尔吃（低优先级撞见）」→ 更细
"""
import random

random.seed(191)
STEPS = 600
FOOD_P = 0.15


def run_old(npf):
    """旧看法：NPF=直接驱动找食物"""
    E = 70.0
    found = ate = 0
    for _ in range(STEPS):
        E -= 0.15
        E = max(0.0, E)
        hunger = min(1.0, 1.0 - E / 100.0)
        if random.random() < FOOD_P:
            look = 0.15 + 0.6 * hunger * npf
            if random.random() < look:
                found += 1
                E = min(100.0, E + 6.0)
                ate += 1
    return found, ate


def run_new(npf):
    """新看法：NPF=优先级调制器（饥把食物设为目标）"""
    E = 70.0
    found = ate = 0
    for _ in range(STEPS):
        E -= 0.15
        E = max(0.0, E)
        hunger = min(1.0, 1.0 - E / 100.0)
        # 优先级：食物优先级受 NPF 调制（npf=0 → 优先级不调制=无法把食物设为目标）
        food_priority = 0.15 + 0.6 * hunger * npf
        if random.random() < FOOD_P:
            # 主动找：要有「调制后的优先级」才成立（npf=0 → 0，不主动）
            look = food_priority if npf else 0.0
            if random.random() < look:
                found += 1
                ate += 1
                E = min(100.0, E + 6.0)
            elif random.random() < 0.03:  # 撞见：低优先级偶尔撞上
                found += 1
                ate += 1
                E = min(100.0, E + 2.0)
    return found, ate


def main():
    print('=' * 62)
    print(' 果蝇新看法（优先级调制）vs 旧看法（驱动）')
    print('=' * 62)
    for name, npf in [('野生型', 1), ('NPF敲除', 0)]:
        f_old, a_old = run_old(npf)
        f_new, a_new = run_new(npf)
        print(f'{name}:')
        print(f'  旧看法(驱动): 找{f_old} 吃{a_old}')
        print(f'  新看法(优先级): 找{f_new} 吃{a_new}')
    print()
    print('判据（新看法成立的条件）：')
    print(' 1. 野生型：优先级调制 → 主动找食物（找多）')
    print(' 2. NPF敲除：优先级不调制 → 不主动找，但低优先级偶尔撞见吃')
    print('    ⇒ 新看法能解释「不找但偶尔吃」；旧看法解释不了（要么找要么不找）')
    print(' 3. 若两模型对 NPF 突变表型无差 → 新看法只是旧看法的换名')


if __name__ == '__main__':
    main()
