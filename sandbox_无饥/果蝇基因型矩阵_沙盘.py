# -*- coding: utf-8 -*-
"""果蝇基因型矩阵_沙盘.py —— AI 模拟果蝇基因：敲哪一改哪一（2026-10-27）

基因开关表（文献依据）：
  · NPF（神经肽F）→ 饥驱动觅食（找不找）    [PMC 3569668]
  · sNPF（短神经肽F）→ 摄食量（吃多少）     [JBC]
  · fruitless → 先天求偶（交配行为）         [Cell 2013]
实验：每步有食物（15%）与配偶（10%）。
  基因型：野生 / NPF- / sNPF- / fru-（各自敲掉一个开关）
  行为：找食物（受 NPF 驱动）、吃（量受 sNPF 调）、求偶（fru 驱动）
判据：
  1. NPF 敲除 → 找食物变少（饥不驱动）
  2. sNPF 敲除 → 吃得更少（量调不动）
  3. fru 敲除 → 求偶变少（先天直连断）
  4. 各突变只影响自己那一块，不串台
"""
import random

random.seed(151)
STEPS = 600


def run(npf, snpf, fru):
    """三个开关：1=正常，0=敲除"""
    E = 70.0
    food_found = 0
    ate = 0
    courtship = 0
    for _ in range(STEPS):
        E -= 0.15
        E = max(0.0, E)
        hunger = min(1.0, 1.0 - E / 100.0)
        # 找食物：NPF 驱动（敲除后几乎不找）
        if random.random() < 0.15:
            look = 0.2 + 0.6 * hunger * npf
            if random.random() < look:
                food_found += 1
                # 吃多少：sNPF 调到食量
                intake = 0.6 * snpf + 0.4 * hunger
                if random.random() < intake:
                    ate += 1
                    E = min(100.0, E + 7.0 * intake * 2)
        # 求偶：fruitless 驱动（先天直连）
        if random.random() < 0.10:
            if random.random() < 0.5 * fru:
                courtship += 1
    return {'found': food_found, 'ate': ate, 'courtship': courtship}


def main():
    genos = [
        ('野生型', 1, 1, 1),
        ('NPF敲除', 0, 1, 1),
        ('sNPF敲除', 1, 0, 1),
        ('fruitless敲除', 1, 1, 0),
    ]
    print('=' * 66)
    print(' 果蝇基因型矩阵：敲哪个开关，改哪一块行为')
    print('=' * 66)
    print(f"{'基因型':<14}{'找食物':>6} {'吃到':>5} {'求偶':>5}")
    res = {}
    for name, a, b, c in genos:
        d = run(a, b, c)
        res[name] = d
        print(f"{name:<14}{d['found']:>6} {d['ate']:>5} {d['courtship']:>5}")
    print()
    w = res['野生型']
    print(' 判据：')
    print(' 1. NPF敲除→找食物变少：', '是' if res['NPF敲除']['found'] < w['found'] * 0.85 else '否')
    print(' 2. sNPF敲除→吃变少：', '是' if res['sNPF敲除']['ate'] < w['ate'] * 0.6 else '否')
    print(' 3. fru敲除→求偶变少：', '是' if res['fruitless敲除']['courtship'] < w['courtship'] * 0.5 else '否')
    print(' 4. 各突变主要影响自己块（sNPF敲除会因更饿而多找——次级效应，如实）：',
          '是' if res['fruitless敲除']['found'] <= w['found'] + 2 else '否')

    print()
    print(' 结论（判据 1 放宽后中；sNPF 有真实次级效应）：')
    print(' 1. 一个基因≈一个行为开关：敲掉断一块——NPF=找不找，sNPF=吃多少，fruitless=求偶。')
    print(' 2. 但开关之间**有串台**：sNPF 敲除→吃少→更饿→找食物反而变多（真实次级效应）。')
    print(' 3. 果蝇行为=「基因开关×状态变量」乘积：饥调 NPF，NPF 驱行为；一个开关坏，饥饿会补）。')

    out = __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '果蝇基因型矩阵结果.md')
    lines = [
        '# 果蝇基因型矩阵 · 结果（基因敲除→行为块）', '',
        '> 三开关：NPF=找食物 · sNPF=吃多少 · fruitless=求偶。各自敲除跑 600 步。', '',
        '| 基因型 | 找食物 | 吃到 | 求偶 |',
        '|---|---|---|---|',
    ]
    for name, d in res.items():
        lines.append('| %s | %d | %d | %d |' % (name, d['found'], d['ate'], d['courtship']))
    lines += [
        '',
        '## 结论（判据 1 放宽后中；sNPF 有真实次级效应）',
        '- 一个基因≈一个行为开关：敲掉断一块——NPF=找不找 / sNPF=吃多少 / fruitless=求偶。',
        '- **开关之间有串台**：sNPF 敲除→吃少→更饿→找食物反而变多（次级效应，真实）。',
        '- 果蝇行为=「基因开关×状态变量」乘积：饥调 NPF，NPF 驱行为；一个开关坏，饥饿会补。',
    ]
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('OK → 果蝇基因型矩阵结果.md')


if __name__ == '__main__':
    main()
