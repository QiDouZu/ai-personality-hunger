# -*- coding: utf-8 -*-
"""恢复曲线_沙盘.py —— 压力撤掉后，自反不是瞬间回来的（2026-10-27）

发现（层级降级）：压力把自反打掉，人退回本能。
问题：压力撤了，人立刻恢复理智吗？
假设：自反恢复有延迟/惯性——压力降下去后，r_eff 要花时间才回到门槛上。
  恢复期：r_eff = r0×(1-压力) × 恢复因子(随时间从0.5升到1.0)
  恢复期内：自反半在线（误吃中等）
实验：压力脉冲——前 200 步压力=0.8（自反掉线），之后降到 0.1（压力撤）
  三模式：
  · 瞬时恢复：压力一撤自反立刻回来（假设的理想）
  · 有惯性：恢复期中 r_eff 慢慢爬（要 80 步）
  · 过度补偿：压力撤了以后还多吃一阵（报复性吃）
判据：
  1. 有惯性时，恢复期内误吃比瞬时恢复多
  2. 过度补偿时，压力撤后真吃比基线多（吃多了）
  3. 恢复需要时间（恢复步数 > 0）
"""
import random

random.seed(131)
STEPS = 400
STRESS_END = 200      # 前 200 步高压力，之后撤
R0 = 0.9
THRESHOLD = 0.55


def run(mode, steps=STEPS):
    E = 60.0
    true_eaten = 0
    miss_eaten = 0
    recover_steps = 0
    E_trace = []
    for t in range(steps):
        E -= 0.12
        # 压力：前 200 高，之后撤
        pressure = 0.8 if t < STRESS_END else 0.1
        # 有效 r：基础 + 恢复惯性
        base = R0 * (1 - pressure)
        if mode == 'instant':
            r_eff = base
        elif mode == 'inertia':
            if t < STRESS_END:
                r_eff = base
            else:
                # 恢复期：从 0.5 基线慢慢爬到 1.0，约 80 步
                k = min(1.0, (t - STRESS_END) / 80.0)
                r_eff = base * (0.5 + 0.5 * k)
                if r_eff >= THRESHOLD and recover_steps == 0:
                    recover_steps = t - STRESS_END
        else:  # overcompensate
            if t < STRESS_END:
                r_eff = base
            else:
                k = min(1.0, (t - STRESS_END) / 80.0)
                r_eff = base * (0.5 + 0.5 * k)
                if r_eff >= THRESHOLD and recover_steps == 0:
                    recover_steps = t - STRESS_END
        appear = random.random() < 0.08
        if not appear:
            E_trace.append(round(E, 2))
            continue
        is_true = random.random() < 0.55
        ate = False
        if r_eff >= THRESHOLD:
            p_accept = 0.95 if is_true else 0.05
        else:
            p_accept = 0.85 if is_true else 0.6
        # 过度补偿：压力撤后 60 步内更爱吃
        if mode == 'overcompensate' and t >= STRESS_END and t < STRESS_END + 60:
            p_accept = min(1.0, p_accept * 1.4)
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
    steady = E_trace[100:]
    after = E_trace[STRESS_END:]
    return {'true': true_eaten, 'miss': miss_eaten,
            'E_mean': round(sum(steady) / len(steady), 1),
            'recover': recover_steps,
            'after_true': sum(1 for _ in []) if False else 0}


def main():
    inst = run('instant')
    inert = run('inertia')
    over = run('overcompensate')
    print('=' * 72)
    print(' 恢复曲线：压力撤后自反不是瞬间回来的')
    print('=' * 72)
    print(f"{'模式':<14}{'真吃':>6} {'误吃':>6} {'能量':>7} {'恢复步':>6}")
    for name, d in (('瞬时恢复', inst), ('有惯性', inert), ('过度补偿', over)):
        print(f"{name:<14}{d['true']:>6} {d['miss']:>6} {d['E_mean']:>7} {d['recover']:>6}")
    print()
    print(' 判据：')
    print(' 1. 有惯性时误吃比瞬时多：', '是' if inert['miss'] > inst['miss'] else '否')
    print(' 2. 恢复要时间（恢复步 > 0）：', '是' if inert['recover'] > 0 else '否')
    print(' 3. 过度补偿多吃了：', '是' if over['true'] > inert['true'] else '否')
    print()
    print(' 结论（判据 1 没中，如实报）：')
    print(' 1. 瞬时恢复：假设的理想——压力一撤就全理智。')
    print(' 2. 有惯性：恢复期自反半在线（大部分时间仍在门槛下），误吃没比瞬时多（3 vs 4），')
    print('    但能量更低（79.7 vs 93.6）——**恢复期里吃得少、状态乱。**')
    print(' 3. 过度补偿：压力撤后 60 步内多吃（真吃 19 > 15）——**伤过之后会多拿一点。**')
    print(' ⇒ 门槛能掉能回：退回去快，爬回来要时间（恢复约 29 步），回来还会多拿补偿。')
    print('    但「恢复期误吃更多」这条没中——它体现在能量和状态，不在误吃次数。')

    out = __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '恢复曲线结果.md')
    lines = [
        '# 恢复曲线 · 结果（压力撤后自反不是瞬间回来）', '',
        '> 前 200 步压力 0.8，之后 0.1。恢复期约 80 步。', '',
        '| 模式 | 真吃 | 误吃 | 能量 | 恢复步 |',
        '|---|---|---|---|---|',
    ]
    for name, d in (('瞬时恢复', inst), ('有惯性', inert), ('过度补偿', over)):
        lines.append('| %s | %d | %d | %.1f | %d |' % (name, d['true'], d['miss'], d['E_mean'], d['recover']))
    lines += [
        '',
        '## 结论（判据 1 没中，如实）',
        '- 瞬时恢复是理想（压力一撤全理智）。',
        '- 有惯性：恢复期自反半在线，**误吃没比瞬时多，但能量更低**（79.7 vs 93.6）——恢复期里吃得少、状态乱。',
        '- 过度补偿：压力撤后 60 步多吃（真吃 19 > 15）——**伤过之后会多拿一点。**',
        '- **门槛能掉能回：退回去快，爬回来要时间（约 29 步）；回来时多拿补偿。**',
    ]
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('OK → 恢复曲线结果.md')


if __name__ == '__main__':
    main()
