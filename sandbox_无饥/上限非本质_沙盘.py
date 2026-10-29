# -*- coding: utf-8 -*-
"""上限非本质_沙盘.py —— 同一机制，只变生长速度(上限)，看是连续还是跳变（2026-10-27）

祈祷主：人的区别在于上限，不是本质区别；更是「生长速度」——人慢为大脑发育，动物快但锁死。
验证：同一套机制（本能+思想×输入），只变生长速度（=发育停止点：慢=晚停，快=早停），
看表现是「连续爬升」还是「本质跳变」（无断崖→区别=上限，同本质刻度不同）。
"""
import random

random.seed(261)
STEPS = 400


def run(stop, cap, seed):
    random.seed(seed)
    E = 70.0
    learned = 0
    for t in range(STEPS):
        E -= 0.2
        E = max(0.0, E)
        if random.random() < 0.1:
            if t < stop:
                p = min(1.0, (t / stop) * cap)
                learned += 1 if random.random() < p else 0
            else:
                learned += 1 if random.random() < cap * 0.3 else 0
    return learned


def run_avg(stop, cap):
    """多 seed 平均，去掉随机噪声"""
    vals = [run(stop, cap, s) for s in range(8)]
    return sum(vals) / len(vals)


def main():
    print('=' * 64)
    print(' 同一机制，只变发育停止（上限）——连续还是跳变？（8 seed 平均）')
    print('=' * 64)
    pts = [(60, 0.2), (100, 0.35), (140, 0.5), (180, 0.65),
           (220, 0.8), (260, 0.85), (300, 0.9)]
    print(f'{"停止点":>6} {"上限":>6} {"平均学习":>8}')
    for stop, cap in pts:
        print(f'{stop:>6} {cap:>6.2f} {run_avg(stop, cap):>8.1f}')
    print()
    print('判据：')
    print(' 若学习随停止点连续爬升（无断崖）→ 区别=上限（同一本质，刻度不同）')
    print(' ⇒ 预期连续 → 支持「人的区别在上限，不是本质区别」')


if __name__ == '__main__':
    main()
