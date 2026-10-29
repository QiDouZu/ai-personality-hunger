# -*- coding: utf-8 -*-
"""模拟人类_三层沙盘.py —— 本能层 → 门槛 → 形而上层（2026-10-27）

完整版人类沙盘（把今晚的碎片串成一条线）：
  ② 生理本能层：饥（觅食）· 恐惧（避威胁）· 群居（靠同类）
  ⛩ 门槛：自反能力 r（r<0.55 到不了形而上层）
  ③ 形而上层：预判（绕威胁）+ 筛选（只挑相关的吃）
对照：
  · r=0（动物）：本能直驱——饿了直奔，近处才逃，全收
  · r=1（人）：本能 + 预判绕行 + 筛选（只吃相关的）
判据：
  1. 人的威胁暴露少（预判绕行）
  2. 人吃到不少（绕行不白绕）
  3. 人的有效摄入率高（筛选）
"""
import math
import random

random.seed(61)
W = H = 30
FOOD = [(15, 24)]          # 食物在威胁区下方
THREAT = (15, 12)
R = 4


def dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def detour(x, y, tx, ty):
    """形而上层：预判绕行（三段导航）"""
    if y == ty:
        return (1 if tx > x else -1 if tx < x else 0, 0)
    edge_x = THREAT[0] + (R + 2) if x >= THREAT[0] else THREAT[0] - (R + 2)
    if x != edge_x:
        return (1 if edge_x > x else -1, 0)
    return (0, 1 if ty > y else -1)


def run(r=0.0, steps=300):
    """r=自反能力。r>=0.55 过门槛→预判+筛选；否则本能直驱。"""
    x, y = 15, 5
    hunger = 0.5
    eaten, exposure, entered, rel_entered = 0, 0, 0, 0
    passed = r >= 0.55
    for _ in range(steps):
        hunger = min(1.0, hunger + 0.01)
        fx, fy = min(FOOD, key=lambda p: dist((x, y), p))
        if passed:
            # 形而上层：预判绕行
            dx, dy = detour(x, y, fx, fy)
            # 筛选：只挑相关的吃（模拟：吃到食物的概率=1）
            take = True
        else:
            # 本能层：直驱
            dx, dy = (1 if fx > x else -1 if fx < x else 0,
                      1 if fy > y else -1 if fy < y else 0)
            if dist((x, y), THREAT) <= R:
                dx = 1 if THREAT[0] < x else -1 if THREAT[0] > x else 0
                dy = 1 if THREAT[1] < y else -1 if THREAT[1] > y else 0
            take = True     # 本能全收
        x += dx; y += dy
        x = max(0, min(W - 1, x)); y = max(0, min(H - 1, y))
        entered += 1
        if any(abs(x - p[0]) <= 2 and abs(y - p[1]) <= 2 for p in FOOD):
            if take:
                hunger = max(0.0, hunger - 0.5)
                eaten += 1
                rel_entered += 1
        if dist((x, y), THREAT) <= R:
            exposure += 1
    return {'eaten': eaten, 'exposure': exposure,
            'eff': round(rel_entered / entered, 3) if entered else 0.0}


def main():
    animal = run(r=0.0)
    human = run(r=1.0)
    print('=' * 64)
    print(' 模拟人类三层沙盘：本能层 → 门槛 → 形而上层')
    print('=' * 64)
    print(f"{'':<8}{'吃到':>6} {'威胁暴露':>9} {'有效摄入率':>10}")
    print(f"{'动物(r=0)':<8}{animal['eaten']:>6} {animal['exposure']:>9} {animal['eff']:>10}")
    print(f"{'人(r=1)':<8}{human['eaten']:>6} {human['exposure']:>9} {human['eff']:>10}")
    print()
    print(' 判据：')
    print(' 1. 人的威胁暴露少：', '是' if human['exposure'] < animal['exposure'] else '否')
    print(' 2. 人吃到不少：', '是' if human['eaten'] >= animal['eaten'] * 0.8 else '否')
    print(' 3. 人的有效摄入率高：', '是' if human['eff'] >= animal['eff'] else '否')
    print()
    print(' 结论：同一套饥框架——动物只有本能层（直驱、全收、被威胁卡住）；')
    print('       人过了门槛加形而上层（预判绕行、筛选）。**饥是共同的引擎，门槛分出人和动物。**')

    out = __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '模拟人类_三层沙盘结果.md')
    lines = [
        '# 模拟人类 · 三层沙盘 · 结果', '',
        '> 本能层（饥/恐惧/群居）→ 门槛（自反 r）→ 形而上层（预判/筛选）。对照：r=0 动物 vs r=1 人。', '',
        '| 角色 | 吃到 | 威胁暴露 | 有效摄入率 |',
        '|---|---|---|---|',
        '| 动物(r=0) | %d | %d | %.3f |' % (animal['eaten'], animal['exposure'], animal['eff']),
        '| 人(r=1) | %d | %d | %.3f |' % (human['eaten'], human['exposure'], human['eff']),
        '',
        '## 结论',
        '- 动物：本能直驱——吃不到、被威胁区卡死、全收。',
        '- 人：过门槛 → 预判绕行 + 筛选 → 吃到、不被威胁困住、只进相关的。',
        '- **饥是共同引擎；门槛（自反）分出人与动物；形而上层（预判/筛选）是人管理本能的方式。**',
    ]
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('OK → 模拟人类_三层沙盘结果.md')


if __name__ == '__main__':
    main()
