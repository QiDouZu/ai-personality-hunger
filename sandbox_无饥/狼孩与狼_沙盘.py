# -*- coding: utf-8 -*-
"""狼孩与狼_沙盘.py —— 两函数+输入：最低级的人 vs 最高级的动物（2026-10-27）

祈祷主：变量对人实现大部分、动物小部分、虫子没用，剩下是生理本能。
  用函数叠加判断：狼孩（最低级的人）vs 狼（最高级的动物）。

模型：
  生物 = 本能函数（反射/生存） + 思想函数（判断） × 输入（社会化/语言）
  狼   ：本能高（0.8），思想上限低（0.2），输入自带（本能内嵌）
  狼孩 ：本能中（0.5，人本能弱），思想潜力高（0.9），但输入≈0（未社会化）→ 实际思想低
判据：狼孩行为≈狼（都靠本能），但「学习上限」不同——狼孩潜力被剥夺未兑现。
"""
import random

random.seed(231)
STEPS = 500


def run(species):
    if species == 'wolf':
        instinct = 0.8
        thought_pot = 0.2
        input_ = 0.8  # 本能自带输入
    else:  # feral (wolf-child)
        instinct = 0.5
        thought_pot = 0.9
        input_ = 0.05  # 未社会化，输入近零
    # 实际思想 = 潜力 × 输入
    thought_actual = thought_pot * input_
    E = 70.0
    forage = danger_avoid = learned = 0
    for _ in range(STEPS):
        E -= 0.2
        E = max(0.0, E)
        if random.random() < 0.15:
            # 找食：本能主导
            if random.random() < instinct * 0.7 + thought_actual * 0.3:
                forage += 1
                E = min(100.0, E + 5.0)
        if random.random() < 0.1:
            # 危险规避：本能主导（狼 vs 狼孩都强）
            if random.random() < 0.7 * (instinct + 0.2):
                danger_avoid += 1
        if random.random() < 0.1:
            # 学习/模仿：思想函数主导（狼孩几乎不学）
            if random.random() < thought_actual * 0.8:
                learned += 1
    return dict(instinct=instinct, thought_pot=thought_pot, input_=input_,
                thought_actual=thought_actual, forage=forage,
                danger_avoid=danger_avoid, learned=learned)


def main():
    print('=' * 64)
    print(' 狼孩 vs 狼（两函数+输入）')
    print('=' * 64)
    for name, sp in [('狼(最高级动物)', 'wolf'), ('狼孩(最低级的人)', 'feral')]:
        r = run(sp)
        print(f'{name}: 本能{r["instinct"]} 思想潜力{r["thought_pot"]} 输入{r["input_"]:.2f}')
        print(f'   实际思想={r["thought_actual"]:.2f} 找食{r["forage"]} 避险{r["danger_avoid"]} 学习{r["learned"]}')
    # 对照：狼孩若给输入（回归社会）
    r2 = run('wolf')
    print()
    print('【对照】狼孩若给输入（回归社会 0.8）：')
    inst = 0.5; pot = 0.9; inp = 0.8
    actual = pot * inp
    print(f'   实际思想={actual:.2f}（潜力0.9×输入0.8）→ 思想函数跳起来')
    print()
    print('判据：')
    print(' 1. 找食/避险：两者相近（都靠本能）')
    print(' 2. 学习：狼≈0，狼孩也≈0（输入近零）→ 行为上难分')
    print(' 3. 但狼孩=「潜力高但被剥夺」：若给输入，思想函数会跳——这才是「最低级的人 vs 最高级动物」的差')
    print(' ⇒ 区别不在当前行为，在「输入回补后的学习上限」')


if __name__ == '__main__':
    main()
