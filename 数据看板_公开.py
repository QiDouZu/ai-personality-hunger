# -*- coding: utf-8 -*-
"""数据看板.py —— 实时汇总所有饥实验的最新数据（2026-10-27）

祈祷主：「将这份数据尝试实时更新」。每跑一次，重算全部实验、刷新
`数据看板.md` + `数据看板.json`（带时间戳），这就是「实时」。

覆盖实验（不依赖真实库的纯计算 + 依赖真实库的生存/自恋冲突）：
  1. 双反馈实验：单反馈 vs 双反馈
  2. 辩证适应实验：Q 钉死 vs Q 随能力涨
  3. 证伪扫描：三个条件的关键临界点（q_per_d / r_drop / g）
  4. 矛盾生存实验：强/弱模式（真实矛盾源）
  5. 双自恋冲突实验：单变量 vs 双变量（真实矛盾源）
"""
import os
import sys
import json
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'experiments'))

OUT_MD = os.path.join(HERE, '数据看板_公开.md')
OUT_JSON = os.path.join(HERE, '数据看板_公开.json')


def collect():
    rows = []
    # ---- 1. 双反馈 ----
    import 双反馈实验 as D
    for name, dual in [('双反馈·单反馈（只长本事）', False), ('双反馈·双反馈（长本事+缓解）', True)]:
        r = D.run(name, dual)
        rows.append({'实验': '双反馈', '方案': r['name'], '结局': r['status'],
                     '轮次': r['died_at'] or '—', '能力D': r['D'], '匮乏L': r['L'], '解掉': r['solved']})

    # ---- 2. 辩证适应 ----
    import 辩证适应实验 as B
    for name, ad in [('辩证·不适配（Q钉死）', False), ('辩证·自适应（Q随D涨）', True)]:
        r = B.run(name, ad)
        rows.append({'实验': '辩证适应', '方案': r['name'], '结局': r['status'],
                     '轮次': r['died_at'] or '—', '能力D': r['D'], '原初P': r['P'], '阈值Q': r['Q'], '匮乏L': r['L']})

    # ---- 3. 证伪扫描（关键临界点） ----
    import 证伪扫描 as F
    for label, kw in [
        ('证伪·q_per_d=0.4（低于临界）', {'q_per_d': 0.4, 'r_drop': 0.1, 'g': 0.15}),
        ('证伪·q_per_d=0.5（过临界）', {'q_per_d': 0.5, 'r_drop': 0.1, 'g': 0.15}),
        ('证伪·r_drop=0.06（回补不足）', {'q_per_d': 0.8, 'r_drop': 0.06, 'g': 0.15}),
        ('证伪·r_drop=0.15（回补过量）', {'q_per_d': 0.8, 'r_drop': 0.15, 'g': 0.15}),
        ('证伪·g=0.05（能力不足）', {'q_per_d': 0.8, 'r_drop': 0.1, 'g': 0.05}),
    ]:
        status, t = F.run(**kw)
        rows.append({'实验': '证伪扫描', '方案': label, '结局': status, '轮次': t or '—'})

    # ---- 4. 矛盾生存（真实库，可能略慢） ----
    try:
        import 沙盘 as S
        import 矛盾生存实验 as M
        sources = S.find_pairs_dedup(S.load_entries(), limit=10 ** 6)
        r_strong = M.run('强模式', M.STRONG, sources)
        r_weak = M.run('弱模式', M.WEAK, sources)
        for name, r in [('矛盾生存·强（+1.0/矛盾）', r_strong), ('矛盾生存·弱（+0.1/矛盾）', r_weak)]:
            rows.append({'实验': '矛盾生存', '方案': name, '结局': r['status'],
                         '轮次': r['died_at'] or '—', '峰值': r['peak']})
    except Exception as e:
        rows.append({'实验': '矛盾生存', '方案': '（跑真实库失败，跳过）', '结局': 'ERR: %s' % e, '轮次': '—'})

    # ---- 5. 双自恋冲突（真实库） ----
    try:
        import 双自恋冲突实验 as Z
        sources = S.find_pairs_dedup(S.load_entries(), limit=10 ** 6)
        r_single = Z.run_single(sources)
        r_dual = Z.run_dual(sources)
        for name, r in [('双自恋·单变量', r_single), ('双自恋·双变量', r_dual)]:
            rows.append({'实验': '双自恋冲突', '方案': name, '结局': r['status'],
                         '轮次': r['died_at'] or '—', '峰值': r['peak']})
    except Exception as e:
        rows.append({'实验': '双自恋冲突', '方案': '（跑真实库失败，跳过）', '结局': 'ERR: %s' % e, '轮次': '—'})

    return rows


def render(rows):
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    lines = [
        '# 数据看板（实时·重跑即刷新）\n',
        '> 生成时间：**%s** ｜ 重跑：`python 数据看板.py`\n' % ts,
        '> 每个方案都挂着「怎么推翻我」——见 `证伪判据总表.md`。\n',
        '',
        '| 实验 | 方案 | 结局 | 轮次 | 关键数 |',
        '|---|---|---|---|---|',
    ]
    for r in rows:
        nums = []
        for k in ('能力D', '原初P', '阈值Q', '匮乏L', '解掉', '峰值'):
            if k in r:
                nums.append('%s=%s' % (k, r[k]))
        lines.append('| %s | %s | %s | %s | %s |' % (
            r['实验'], r['方案'], r['结局'], r['轮次'], ' '.join(nums) or '—'))
    lines += [
        '',
        '## 读法\n',
        '- **活** = 抗压+快乐同长；**压抑崩溃** = 痛苦没被填补；**无欲无求** = 回补过量麻木；**饿死** = 矛盾顶穿生存线。',
        '- 证伪扫描三行是「条件边界」：越过临界行为翻转 = 假设被推翻。',
        '',
        '## 关于个人饥数据\n',
        '- **本仓库不含任何真实饥数据**（没有当前饥、没有掌控序列、没有心跳账本）。',
        '- 公开的是：模型、公式、实验方法、结果表、证伪条件。',
    ]
    return '\n'.join(lines)


def main():
    rows = collect()
    md = render(rows)
    with open(OUT_MD, 'w', encoding='utf-8') as f:
        f.write(md)
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump({'time': time.strftime('%Y-%m-%dT%H:%M:%S'), 'rows': rows}, f, ensure_ascii=False, indent=1)
    print(md)
    print('\n落盘: %s' % OUT_MD)


if __name__ == '__main__':
    main()
