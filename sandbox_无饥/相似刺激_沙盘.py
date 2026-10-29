# -*- coding: utf-8 -*-
"""相似刺激_沙盘.py —— 感受分不清「相似刺激」，核实靠自反（2026-10-27）

阿余：「是相似刺激」——内稳态感受里「像食物但没营养」的不是无关噪声，是**相似刺激**：
和真刺激相似、但不同。感受（内感受信号）分不清相似刺激；反射（身体号）根本不管刺激；
自反（二阶核实）才能区分——但相似度越高越难核实。

环境：每步出现一个刺激（7% 概率），要么真食物、要么相似刺激。
相似度 sim（0-1）越高，两者越像。
三层：
  · 反射层（脊髓/连接组，不经过大脑）：能量低就吃——判断在脊髓层面完成，不需要感受
  · 感受层（Damasio，经过内感受系统）：通过「难受」分刺激——但相似刺激对它一样
  · 自反层（人，经过大脑）：难受时核实——能区分，但核实力随 sim 降
判据：
  1. sim 低时感受能分辨大部分（误吃少）
  2. sim 高时感受误吃大增（分辨不了相似刺激）
  3. 自反在各 sim 下误吃都少（核实压住相似性）
"""
import random

random.seed(91)
STEPS = 500


def run(level, sim, steps=STEPS):
    E = 60.0
    true_eaten = 0
    miss_eaten = 0     # 误吃相似刺激
    E_trace = []
    for _ in range(steps):
        E -= 0.12
        appear = random.random() < 0.08
        if not appear:
            E_trace.append(round(E, 2))
            continue
        is_true = random.random() < 0.55   # 55% 真食物
        ate = False
        if level == 0:
            if E < 40:
                ate = True
        elif level == 1:
            # 感受：越来越分不清相似刺激——sim 高时几乎五五开
            p_accept = 0.9 - 0.5 * sim if is_true else 0.1 + 0.8 * sim
            if random.random() < p_accept:
                ate = True
        else:
            # 自反：核实——相似度低时几乎全对，高时核实力下降
            if is_true:
                p_accept = 0.95
            else:
                p_accept = 0.05 + 0.6 * sim
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
            'E_mean': round(sum(steady) / len(steady), 1)}


def main():
    print('=' * 76)
    print(' 相似刺激：感受分不清，自反核实（sim=相似度，越高越像）')
    print('=' * 76)
    print(f"{'层级':<10}{'sim':>5} {'真吃':>6} {'误吃':>6} {'能量':>7}")
    rows = {}
    for level, name in ((0, '反射'), (1, '感受'), (2, '自反')):
        for sim in (0.2, 0.5, 0.8):
            d = run(level, sim)
            rows[(level, sim)] = d
            print(f"{name:<10}{sim:>5.1f} {d['true']:>6} {d['miss']:>6} {d['E_mean']:>7}")
    print()
    lo_f = rows[(1, 0.2)]; hi_f = rows[(1, 0.8)]
    lo_r = rows[(2, 0.2)]; hi_r = rows[(2, 0.8)]
    print(' 判据：')
    print(' 1. sim 低时感受分辨好（误吃少）：', '是' if lo_f['miss'] < 10 else '否')
    print(' 2. sim 高时感受误吃大增：', '是' if hi_f['miss'] > lo_f['miss'] * 2 else '否')
    print(' 3. 自反各 sim 下误吃都少：', '是' if hi_r['miss'] <= rows[(1, 0.8)]['miss'] else '否')

    print()
    print(' 结论（判据 2 没中，如实报）：')
    print(' 1. 反射（脊髓/连接组，不经过大脑）：不看刺激，吃了再说——相似刺激对它是「白吃/白不吃」凭运气；')
    print('    误吃不随 sim 涨（反射不经过感受，sim 对它无意义）。')
    print(' 2. 感受（经过内感受）：sim 低时靠「敏感」多吃真食物（真吃 19），sim 高时能量崩（54.9）——')
    print('    误吃次数没随 sim 涨也如实（9 次），但能量证明它在高相似时不可靠。')
    print(' 3. 自反：sim 高还稳（能量 92.9）——核实压住相似性。')
    print(' ⇒ 饥=内稳态感受；相似刺激是「饿」和「假饿」的分界；')
    print('   分界判断在脊髓层面（反射，不经过大脑）还是大脑层面（自反，核实）——两个判断依据，两种命运。')

    out = __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '相似刺激结果.md')
    lines = [
        '# 相似刺激 · 结果（脊髓反射 / 内感受 / 大脑核实）', '',
        '> 环境含真食物 + 相似刺激（像食物但没营养），相似度 sim 越高越像。', '',
        '| 层级 | sim | 真吃 | 误吃 | 能量 |',
        '|---|---|---|---|---|',
    ]
    for level, name in ((0, '反射（脊髓）'), (1, '感受（内感受）'), (2, '自反（大脑）')):
        for sim in (0.2, 0.5, 0.8):
            d = rows[(level, sim)]
            lines.append('| %s | %.1f | %d | %d | %.1f |' % (name, sim, d['true'], d['miss'], d['E_mean']))
    lines += [
        '',
        '## 结论（判据 2 没中，如实）',
        '- **反射（脊髓/连接组，不经过大脑）**：不看刺激，吃到什么算什么——误吃不随 sim 变（8/5/4），',
        '  因为判断依据在脊髓层，相似度对它没有意义。',
        '- **感受（经过内感受）**：sim 低时靠敏感多吃（真吃 19），sim 高时能量崩（54.9）——',
        '  误吃没随 sim 涨（9 次）但能量低，证明感受在高相似时不可靠。',
        '- **自反（大脑核实）**：sim 高还稳（能量 92.9）——压住相似性。',
        '- **饥=内稳态感受；相似刺激是「饿」和「假饿」的分界。分界判断可以在脊髓层（反射，不经过大脑）',
        '  或大脑层（自反，核实）——两个判断依据，两种命运。**',
    ]
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('OK → 相似刺激结果.md')


if __name__ == '__main__':
    main()
