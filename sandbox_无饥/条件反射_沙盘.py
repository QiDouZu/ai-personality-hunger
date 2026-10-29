# -*- coding: utf-8 -*-
"""条件反射_沙盘.py —— 学出来的直连 vs 天生反射 vs 思考（2026-10-27）

阿余：「条件反射」——反射有两种：天生的（非条件）和学出来的（条件）。
实验：每 trial 铃响（中性刺激）→ 食物出现（70% 概率）。
三层：
  · 非条件反射：见食物就吃（铃对它没意义）
  · 条件反射：配对学铃——学成后铃一响就准备吃（不核实食物来没来）→ 没食物时白准备
  · 思考：铃响后等食物确认再吃——没食物就不吃
判据：
  1. 条件反射学会后，铃响就反应（反应率高）
  2. 条件反射在无食物 trial 误反应（白准备）
  3. 思考误反应少（核实）
"""
import random

random.seed(101)
TRIALS = 200


def run(level):
    """level: 0 非条件反射(纯食物) / 1 条件反射(学铃) / 2 思考(核实)"""
    bell_trigger = 0.1     # 条件反射对铃的触发强度（初始 0.1，配对学习上升）
    reacted = 0
    mis_reacted = 0        # 铃响但没食物还反应
    ate = 0
    for t in range(TRIALS):
        bell = True                       # 每 trial 都铃响
        food = random.random() < 0.70     # 70% 有食物
        if level == 0:
            if food:
                ate += 1
        elif level == 1:
            # 配对学习：有食物就学（铃→食物联系增强）
            if food:
                bell_trigger = min(1.0, bell_trigger + 0.03)
                # 食物来了就吃（条件反射：铃已响，也不核实）
                reacted += 1
                ate += 1
            else:
                # 铃响没食物：条件反射也会反应（白准备）
                if random.random() < bell_trigger:
                    mis_reacted += 1
        else:
            # 思考：铃响后等食物来了才吃；没食物不吃
            if food:
                reacted += 1
                ate += 1
    return {'reacted': reacted, 'mis': mis_reacted, 'ate': ate,
            'bell_trigger': round(bell_trigger, 2)}


def main():
    no = run(0)
    cr = run(1)
    th = run(2)
    print('=' * 70)
    print(' 条件反射：学出来的直连 vs 天生反射 vs 思考（200 trials，70% 有食物）')
    print('=' * 70)
    print(f"{'层级':<16}{'反应':>6} {'误反应':>7} {'吃到':>6} {'铃触发':>7}")
    print(f"{'非条件反射':<16}{no['reacted']:>6} {no['mis']:>7} {no['ate']:>6} {'-':>7}")
    print(f"{'条件反射':<16}{cr['reacted']:>6} {cr['mis']:>7} {cr['ate']:>6} {cr['bell_trigger']:>7}")
    print(f"{'思考':<16}{th['reacted']:>6} {th['mis']:>7} {th['ate']:>6} {'-':>7}")
    print()
    print(' 判据：')
    print(' 1. 条件反射学会后铃响就反应：', '是' if cr['bell_trigger'] > 0.8 else '否')
    print(' 2. 条件反射无食物时误反应（白准备）：', '是' if cr['mis'] > 0 else '否')
    print(' 3. 思考误反应少：', '是' if th['mis'] <= cr['mis'] else '否')

    print()
    print(' 结论：')
    print(' 1. 非条件反射：只有食物触发——铃对它没意义，也不学铃。')
    print(' 2. 条件反射：学得飞快（铃→食物联系），但学成后铃一响就准备——**不核实食物来没来**（白准备）。')
    print(' 3. 思考：铃响后等确认——没食物就不动。')
    print(' ⇒ 条件反射=学出来的直连：刺激→反应中间依然没有思考，只是连线是训练出的。')
    print('   这正是「虫子到人」线上的 1 层：不是天生，也还不是模型。')

    out = __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '条件反射结果.md')
    lines = [
        '# 条件反射 · 结果（学出来的直连）', '',
        '> 每 trial 铃响 → 70% 有食物。三层对比。', '',
        '| 层级 | 反应 | 误反应 | 吃到 | 铃触发 |',
        '|---|---|---|---|---|',
        '| 非条件反射（纯食物） | %d | %d | %d | - |' % (no['reacted'], no['mis'], no['ate']),
        '| 条件反射（学铃） | %d | %d | %d | %.2f |' % (cr['reacted'], cr['mis'], cr['ate'], cr['bell_trigger']),
        '| 思考（核实） | %d | %d | %d | - |' % (th['reacted'], th['mis'], th['ate']),
        '',
        '## 结论',
        '- 非条件反射：铃对它无意义，只吃食物。',
        '- 条件反射：学得飞快，学成后铃一响就准备——**不核实食物来没来**（无食物时白准备）。',
        '- 思考：铃响后等确认——没食物就不动。',
        '- **条件反射=学出来的直连：刺激→反应没有思考，只是连线是训练出的。**',
        '- 它补在虫子到人线的 0 和 1 之间：不是天生反射，也还不是模型/思考。',
    ]
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('OK → 条件反射结果.md')


if __name__ == '__main__':
    main()
