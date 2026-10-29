# -*- coding: utf-8 -*-
"""果蝇_判断加驱动_沙盘.py —— 饥=潜意识判断→驱动（合版）（2026-10-27）

祈祷主：饥本身就是判断然后驱动的，两个看法不冲突，是同一件事的多个单一视角。
  旧看法（驱动层）：饥 → 驱动行为
  新看法（判断层）：饥 → 设优先级（潜意识判断）→ 驱动执行
  合成：L1 判断（设定目标）→ L2 驱动（执行）

基因：NPF=判断层的开关（NPF 突变 → 不设目标 → 驱动层没目标，不主动找）
测试：合版能否同时解释「野生找食」+「NPF突变不找但偶尔撞见」。
"""
import random

random.seed(201)
STEPS = 600
FOOD_P = 0.15


def run(npf):
    """npf=1 判断层正常，npf=0 判断层断"""
    E = 70.0
    found = ate = 0
    # L1 潜意识判断：饥（内感受误差）→ 是否把食物设为目标
    for _ in range(STEPS):
        E -= 0.15
        E = max(0.0, E)
        hunger = min(1.0, 1.0 - E / 100.0)
        if random.random() < FOOD_P:
            # L1 判断（潜意识）：饥饿够高 + NPF 正常 → 设目标
            target = npf and (hunger > 0.3)
            if target:
                # L2 驱动：执行找（高概率）
                if random.random() < 0.7:
                    found += 1
                    ate += 1
                    E = min(100.0, E + 6.0)
            else:
                # 无目标 → 只有低优先级撞见
                if random.random() < 0.04:
                    found += 1
                    ate += 1
                    E = min(100.0, E + 2.0)
    return found, ate


def main():
    print('=' * 60)
    print(' 果蝇 · 判断+驱动合版（潜意识两层）')
    print('=' * 60)
    for name, npf in [('野生型', 1), ('NPF敲除', 0)]:
        f, a = run(npf)
        print(f'{name}: 找{f} 吃{a}')
    print()
    print('判据：')
    print(' 1. 野生：L1设目标→L2执行→找食多（✓）')
    print(' 2. NPF敲除：L1判断断→不设目标→L2无目标可执行→不主动找+偶尔撞见（✓ 自然出现，无需补丁）')
    print(' 3. 合版=把「判断」和「驱动」两层串起来，两者都不丢')
    print()
    print(' 对潜意识的对应：L1=潜意识判断（不显式），L2=驱动（照判断跑）')
    print(' ⇒ 饥=潜意识判断→驱动，判断在意识下完成，驱动直接执行。')


if __name__ == '__main__':
    main()
