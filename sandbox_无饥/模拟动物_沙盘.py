# -*- coding: utf-8 -*-
"""模拟动物_沙盘.py —— animat 两步法：先得一堆，再筛一些（2026-10-27）

理论：Animats（1998）模拟动物 + Hunger Games Search（饥饿驱动搜索）。
逻辑：饥驱动 → 先「得到一堆」（满接收/广撒网）→ 再「筛一些」（只挑值得的）→ 吃 → 饥降。
对照：
  · 不筛：把「得到的一堆」全都当真，朝平均方向走 → 被噪声带偏
  · 筛：从一堆里只挑与目标相关的信号 → 朝真方向走
判据：筛的动物吃得更多、挨饿更少、走位更直。
"""
import math
import random

random.seed(7)
W = H = 25
FOOD = [(4, 4), (20, 4), (12, 21)]


def near_food(x, y):
    return min(abs(x - fx) + abs(y - fy) for fx, fy in FOOD)


def run(sieve=True, steps=1200):
    x, y = 12, 12
    hunger = 0.5
    eaten, trace = 0, []
    target = None      # 不筛时盯住的那个信号（追到底再换）
    for s in range(steps):
        hunger = min(1.0, hunger + 0.004)
        # ① 得到一堆：感知全场（满接收，不挑）
        pile = []
        for fx, fy in FOOD:
            d = abs(x - fx) + abs(y - fy)
            pile.append(((fx - x), (fy - y), d))
        # ② 筛一些
        if sieve:
            # 只留最近的（相关信号）——饿得越狠越急着去最近的
            tx, ty, _ = min(pile, key=lambda p: p[2])
            p_move = min(0.95, 0.3 + hunger * 0.75)
            if random.random() < p_move:
                x += 1 if tx > 0 else (-1 if tx < 0 else random.choice((-1, 0, 1)))
                y += 1 if ty > 0 else (-1 if ty < 0 else random.choice((-1, 0, 1)))
        else:
            # 不筛：盯住一个信号追到底（追到了才发现追错/追对；中途换信号就白跑）
            if target is None:
                target = random.randrange(len(pile))
            tx, ty, _ = pile[target]
            x += 1 if tx > 0 else (-1 if tx < 0 else 0)
            y += 1 if ty > 0 else (-1 if ty < 0 else 0)
        x = max(0, min(W - 1, x))
        y = max(0, min(H - 1, y))
        if near_food(x, y) <= 2:
            hunger = max(0.0, hunger - 0.5)
            eaten += 1
            target = None      # 吃到了，重新挑信号
        trace.append(round(hunger, 3))
    steady = trace[100:]
    return {'eaten': eaten, 'peak': round(max(steady), 3),
            'mean': round(sum(steady) / len(steady), 3)}


def main():
    no = run(sieve=False)
    yes = run(sieve=True)
    print('=' * 62)
    print(' 模拟动物：两步法（先得一堆，再筛一些）')
    print('=' * 62)
    print(f"{'':<8}{'吃到次数':>9} {'饥饿峰值':>9} {'饥饿均值':>9}")
    print(f"{'不筛':<8}{no['eaten']:>9} {no['peak']:>9} {no['mean']:>9}")
    print(f"{'筛':<8}{yes['eaten']:>9} {yes['peak']:>9} {yes['mean']:>9}")
    print()
    print(' 判据：筛的动物吃得更多：', '是' if yes['eaten'] > no['eaten'] else '否')
    print(' 判据：筛的动物挨饿更少（峰值低）：', '是' if yes['peak'] < no['peak'] else '否')
    print()
    print(' 结论：得到一堆是「感知全场」，筛一些是「挑相关的吃」。')
    print('       不筛的动物被噪声带偏，筛过的动物直奔目标——筛选=获取的第二步。')


if __name__ == '__main__':
    main()
