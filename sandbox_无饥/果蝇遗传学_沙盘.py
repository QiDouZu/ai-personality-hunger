# -*- coding: utf-8 -*-
"""果蝇遗传学_沙盘.py —— 把果蝇遗传学翻译成模型（2026-10-27）

翻译对照（文献 → 模型）：
  · NPF 神经元 = 饥的分子读数 → 模型里「NPF 水平」变量，随饥饿上升
  · 饥饿调制感受（TH-VUM→Gr5a 增益）= 饥改世界的参数 → 模型里「甜信号增益」
  · fruitless/doublesex = 先天直连的基因开关 → 模型里「非条件反射」（基因写死的觅食/回避）
  · 能量传感器（Gr43a）= 饥的读数来源 → 模型里「能量 E」
实验：一只果蝇在含甜/苦食物的环境里找吃的。
  野生型 vs NPF 突变型（NPF=0，饥不驱动觅食）vs 感受增益正常/过载
判据：
  1. 野生型饿时 NPF 高、觅食多、吃到多
  2. NPF 突变型即使很饿也少觅食（饥不驱动）——对应 NPF 沉默
  3. 饥饿时甜增益↑（同一点甜食，饿时吃更多）
"""
import random

random.seed(141)
STEPS = 400


def run(npf_gain=1.0, sweet_gain_base=0.5, mutant=False, steps=STEPS):
    """npf_gain: NPF 强度（突变=0）；sweet_gain_base: 基线甜增益"""
    E = 70.0
    true_eaten = 0
    bitter_eaten = 0
    NPF = 0.0
    npf_sum = 0.0
    E_trace = []
    for _ in range(steps):
        E -= 0.15
        E = max(0.0, E)
        # 饥 → NPF（分子读数），突变型不产 NPF
        NPF = 0.0 if mutant else min(1.0, (1.0 - E / 100.0) * npf_gain)
        npf_sum += NPF
        # 甜/苦信号：饿让甜增益↑（TH-VUM→Gr5a），苦增益跟着 NPF 也变强？
        sweet_gain = sweet_gain_base * (1.0 + 0.9 * NPF)
        # 环境：每步出现食物（15% 甜、5% 苦）
        r = random.random()
        ate = False
        if r < 0.15:   # 甜
            # 觅食：NPF 越高越主动（突变型 NPF=0 就几乎不等——饿了也不找）
            look = 0.05 + 0.6 * NPF if not mutant else 0.02
            if random.random() < look:
                # 吃：甜接受概率随增益涨
                if random.random() < sweet_gain:
                    ate = True
                    E = min(100.0, E + 8.0)
                    true_eaten += 1
        elif r < 0.20:  # 苦
            look = 0.05 + 0.6 * NPF if not mutant else 0.02
            if random.random() < look:
                # 吃：饿时苦也没那么苦（NPF 高时苦接受概率↑——反直觉但文献如此）
                if random.random() < 0.1 + 0.5 * NPF:
                    bitter_eaten += 1
                    E = min(100.0, E + 3.0)
        E_trace.append(round(E, 2))
    steady = E_trace[50:]
    return {'sweet': true_eaten, 'bitter': bitter_eaten,
            'E_mean': round(sum(steady) / len(steady), 1),
            'E_min': min(steady),
            'NPF_final': round(NPF, 2),
            'NPF_mean': round(npf_sum / steps, 2)}


def main():
    wild = run(npf_gain=1.0)
    mutant = run(npf_gain=1.0, mutant=True)
    print('=' * 74)
    print(' 果蝇遗传学沙盘：NPF=饥的分子读数 · 增益=饥改参数 · fruitless=先天直连')
    print('=' * 74)
    print(f"{'类型':<12}{'甜吃':>6} {'苦吃':>6} {'能量均值':>9} {'能量谷':>8} {'NPF均':>7}")
    for name, d in (('野生型', wild), ('NPF突变', mutant)):
        print(f"{name:<12}{d['sweet']:>6} {d['bitter']:>6} {d['E_mean']:>9} {d['E_min']:>8} {d['NPF_mean']:>7}")
    print()
    print(' 判据：')
    print(' 1. 野生型饿时 NPF 高（平均）：', '是' if wild['NPF_mean'] > 0.3 else '否')
    print(' 2. NPF 突变型少觅食（饥不驱动）：', '是' if mutant['sweet'] <= wild['sweet'] * 0.5 else '否')
    print(' 3. 突变型能量更低（吃不到）：', '是' if mutant['E_mean'] < wild['E_mean'] else '否')
    print()
    print(' 结论：')
    print(' 1. 野生型：饿→NPF↑→觅食主动→甜增益↑（同糖更甜）→吃到多。')
    print(' 2. NPF 突变：饿也不觅食、甜增益不升——**饥的分子读数断了，饥就不驱动。**')
    print(' 3. 这就是基因写直连、饥当状态变量调参数的模型版。')

    out = __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '果蝇遗传学结果.md')
    lines = [
        '# 果蝇遗传学 · 沙盘结果（NPF=饥读数）', '',
        '> 野生型 vs NPF 突变型。甜增益=基线×(1+0.9×NPF)。', '',
        '| 类型 | 甜吃 | 苦吃 | 能量均值 | 能量谷 | NPF终 |',
        '|---|---|---|---|---|---|',
        '| 野生型 | %d | %d | %.1f | %.1f | %.2f |' % (wild['sweet'], wild['bitter'], wild['E_mean'], wild['E_min'], wild['NPF_mean']),
        '| NPF突变 | %d | %d | %.1f | %.1f | %.2f |' % (mutant['sweet'], mutant['bitter'], mutant['E_mean'], mutant['E_min'], mutant['NPF_mean']),
        '',
        '## 结论',
        '- 野生型：饿→NPF↑→觅食主动→甜增益↑→吃到多。',
        '- NPF 突变：饿也不觅食、甜增益不升——**饥的分子读数断了，饥就不驱动。**',
        '- 模型版逻辑：基因写直连（fruitless），饥（NPF）当状态变量调参数（增益）。',
        '- 翻译对照：NPF神经元=饥读数 · 甜增益=饥改参数 · 能量传感器=读数来源 · 突变=断线。',
    ]
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('OK → 果蝇遗传学结果.md')


if __name__ == '__main__':
    main()
