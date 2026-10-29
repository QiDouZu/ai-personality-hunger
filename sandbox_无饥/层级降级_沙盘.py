# -*- coding: utf-8 -*-
"""层级降级_沙盘.py —— 门槛不是永久的：压力把自反打掉（2026-10-27）

发现（谱系综合）：自反（形而上层）能核实相似刺激，全程稳。
问题：人是**一直**有自反吗？饿极了、累极了，人会不会退回本能层？
假设：有效自反 r_eff = r × (1 - 压力)，压力 = 疲累/饥饿累积。
  r_eff ≥ 门槛（0.55）：能核实（形而上层）
  r_eff < 门槛：自反掉线，退回本能（反射/感受层）
实验：环境含相似刺激；三档压力（低/中/高）：
  · 低压力：稳在自反层
  · 中压力：部分掉线
  · 高压力：退回反射层
判据：
  1. 低压力误吃少（自反在）
  2. 高压力误吃多（自反掉线）
  3. 有明确阈值（压力超过某值，误吃跳升）
"""
import random

random.seed(121)
STEPS = 600
R_THRESHOLD = 0.55


def run(pressure, r0=0.9, steps=STEPS):
    """r0=基础自反能力；有效 r = r0*(1-pressure)"""
    E = 60.0
    r_eff = r0 * (1 - pressure)
    true_eaten = 0
    miss_eaten = 0
    E_trace = []
    for _ in range(steps):
        E -= 0.12
        appear = random.random() < 0.08
        if not appear:
            E_trace.append(round(E, 2))
            continue
        is_true = random.random() < 0.55
        ate = False
        if r_eff >= R_THRESHOLD:
            # 自反层：核实
            p_accept = 0.95 if is_true else 0.05
        else:
            # 掉线：本能直驱（不核实，见刺激就吃）
            p_accept = 0.85 if is_true else 0.6
        if random.random() < p_accept:
            ate = True
        if ate:
            if is_true:
                E = min(100.0, E + 6.0)
                true_eaten += 1
            else:
                miss_eaten += 1
        E = max(0.0, E)
        E_trace.append(round(E, 2))
    steady = E_trace[50:]
    return {'true': true_eaten, 'miss': miss_eaten,
            'E_mean': round(sum(steady) / len(steady), 1),
            'r_eff': round(r_eff, 2),
            'level': '自反' if r_eff >= R_THRESHOLD else '本能'}


def main():
    print('=' * 74)
    print(' 层级降级：压力把自反打掉（r0=0.9，门槛 0.55）')
    print('=' * 74)
    print(f"{'压力':>5} {'有效r':>6} {'当前层':>6} {'真吃':>6} {'误吃':>6} {'能量':>7}")
    rows = []
    for p in (0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0):
        d = run(p)
        rows.append((p, d))
        print(f"{p:>5.1f} {d['r_eff']:>6.2f} {d['level']:>6} {d['true']:>6} {d['miss']:>6} {d['E_mean']:>7}")
    print()
    lo = rows[0][1]; hi = rows[-1][1]
    print(' 判据：')
    print(' 1. 低压力误吃少（自反在）：', '是' if lo['miss'] <= 10 else '否')
    print(' 2. 高压力误吃多（自反掉）：', '是' if hi['miss'] > lo['miss'] * 3 else '否')
    # 找跳变点
    prev = None
    jump = None
    for p, d in rows:
        if prev is not None and d['level'] != prev[1]['level']:
            jump = (prev[0], p)
            break
        prev = (p, d)
    print(' 3. 有明确阈值（跳变在压力）：', '是' if jump else '否', jump)
    print()
    print(' 结论：')
    print(' 1. 自反不是常驻的——压力（疲倦/饥饿）会把它打折：r_eff = r×(1-压力)。')
    print(' 2. 打过了门槛（0.55），人退回本能：见刺激就吃，误吃暴涨。')
    print(' 3. **饿极了、累极了，人就是动物——门槛能上去，也能掉下来。**')
    print('    这正是饥=平衡枢纽：饥高时自反先断电。')

    out = __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '层级降级结果.md')
    lines = [
        '# 层级降级 · 结果（压力打掉自反）', '',
        '> r0=0.9，门槛 0.55；有效 r = r0×(1-压力)。环境含相似刺激。', '',
        '| 压力 | 有效 r | 当前层 | 真吃 | 误吃 | 能量 |',
        '|---|---|---|---|---|---|',
    ]
    for p, d in rows:
        lines.append('| %.1f | %.2f | %s | %d | %d | %.1f |' % (
            p, d['r_eff'], d['level'], d['true'], d['miss'], d['E_mean']))
    lines += [
        '',
        '## 结论',
        '- 自反不是常驻——压力（疲倦/饥饿）打折：r_eff = r×(1-压力)。',
        '- 打过门槛（0.55）就退回本能：见刺激就吃，误吃暴涨。',
        '- **饿极了、累极了，人就是动物——门槛能上去，也能掉下来。**',
        '- 这正是饥=平衡枢纽：饥高时自反先断电。',
    ]
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('OK → 层级降级结果.md')


if __name__ == '__main__':
    main()
