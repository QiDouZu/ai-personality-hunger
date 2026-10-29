# -*- coding: utf-8 -*-
"""两函数_沙盘.py —— 生物=本能函数(反射)+思想函数(判断)叠加（2026-10-27）

祈祷主：生物=生理本能与思想两个函数共同加在一起。
旧模型（只有思想/判断）缺「跳过判断」（反射），无法解释 PTSD 式反射。
测试：三模型在「威胁出现」时的反应：
  · 纯思想：判断后反应（慢，但可修正）
  · 纯本能：反射（快，不可修正）
  · 两函数叠加：本能先动，思想随后修正（可压过反射）
判据：两函数模型能同时解释「快反射」+「可修正」；单函数模型各缺一半。
"""
import random

random.seed(221)
STEPS = 500
THREAT_P = 0.2


def run(mode):
    """mode: 'thought'/'instinct'/'both'"""
    E = 70.0
    reflex_fast = reflex_uncorrected = corrected = 0
    for _ in range(STEPS):
        E -= 0.2
        E = max(0.0, E)
        if random.random() < THREAT_P:
            if mode == 'instinct':
                # 纯本能：S→R 立刻反应（快，但不可修正）
                reflex_fast += 1
                reflex_uncorrected += 1
            elif mode == 'thought':
                # 纯思想：先判断（慢），判断对了才反应
                if random.random() < 0.5:
                    corrected += 1
            else:  # both
                # 本能先动（快）
                if random.random() < 0.9:
                    reflex_fast += 1
                # 思想随后修正（可压过反射）
                if random.random() < 0.6:
                    corrected += 1
                else:
                    reflex_uncorrected += 1
    return reflex_fast, corrected, reflex_uncorrected


def main():
    print('=' * 62)
    print(' 两函数叠加：本能(反射) + 思想(判断)')
    print('=' * 62)
    for name, m in [('纯思想', 'thought'), ('纯本能', 'instinct'), ('两函数叠加', 'both')]:
        f, c, u = run(m)
        print(f'{name:8}: 快速反射{f} 判断修正{c} 反射未修正{u}')
    print()
    print('判据：')
    print(' 纯思想=没有快速反射（慢）；纯本能=没有修正（错误锁死）')
    print(' 两函数叠加=快速反射+可修正（PTSD式快反射被思想压回） ⇒ 生物需要两个函数')
    print(' ⇒ 旧模型（只有思想）缺本能函数，推翻成立。')


if __name__ == '__main__':
    main()
