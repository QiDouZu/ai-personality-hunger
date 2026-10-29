# -*- coding: utf-8 -*-
"""判断加驱动_谱系_沙盘.py —— 判断层是「与人同行」还是「人独有」？（2026-10-27）

合版发现：饥=判断→驱动两层。
问题：判断层（L1 设优先级）是动物已有、人只是分开，还是人独有？

模型：
  r=0（动物）：判断层=驱动层（一层）——饥直接驱动，没有「独立判断」
  r=1（人）：判断层独立输出「目标」，驱动层再执行——中间隔一层
  对照：威胁刺激出现时
    动物（一层）：威胁=驱动，被吓住（直接反应）
    人（两层）：判断层评估「威胁是否真威胁」→ 驱动层按判断走（可绕行）
判据：r=0 被威胁卡住，r=1 判断后可绕行 → 判断层是「分离」出来的（人独有形态）
"""
import random

random.seed(211)
STEPS = 600
THREAT_P = 0.15
FOOD_P = 0.15


def run(r):
    E = 70.0
    food = threat_blocked = 0
    for _ in range(STEPS):
        E -= 0.15
        E = max(0.0, E)
        hunger = min(1.0, 1.0 - E / 100.0)
        if random.random() < FOOD_P:
            if hunger > 0.3:
                if random.random() < 0.7 * (0.5 + 0.5 * r):  # 人判断层独立后找更准
                    food += 1
                    E = min(100.0, E + 6.0)
        if random.random() < THREAT_P:
            if r == 0:
                # 动物：威胁=直接驱动 → 被卡（这轮吃不到）
                threat_blocked += 1
            else:
                # 人：判断层评估 → 多数判断「威胁可控」绕行
                if random.random() < 0.3:  # 仅部分威胁真正阻断
                    threat_blocked += 1
                # 绕行成功=避开威胁，不补能量（绕开威胁≠吃到饭）
    return food, threat_blocked


def main():
    print('=' * 60)
    print(' 判断加驱动 · 谱系（判断层=分离出来的？）')
    print('=' * 60)
    for name, r in [('动物(r=0,判断=驱动合一)', 0), ('人(r=1,判断层独立)', 1)]:
        f, t = run(r)
        print(f'{name}: 吃到{f} 被威胁阻断{t}')
    print()
    print('判据：动物被威胁卡住多（直接反应）；人判断后可绕行（阻断少）')
    print(' ⇒ 判断层=从「判断=驱动」里分离出来的，人独有形态（虫/人新切面）')


if __name__ == '__main__':
    main()
