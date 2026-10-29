# -*- coding: utf-8 -*-
"""沙盘_接内核测试.py —— 用沙盘真实矛盾对，测饥内核的裁决

背景：沙盘现在的饥 = 「消化就低、挂起就压强」两态，没有四指令（消化/搁置/排斥/爆发）。
微内核定下来后，回路该只报「矛盾对属于哪一级」，裁决归内核。

本测试：
1. 用沙盘真实数据（memory.db 的活跃条目）找候选矛盾对
2. conflict_type（结论/情境/粒度冲突）→ 级别（大事/中事/小事）
3. 喂饥内核 → 四指令
4. 对照沙盘原判（消化/挂起）与内核裁决，看差在哪

可证伪：若「结论冲突」（最重要）被内核判成「消化」（内化了事），
说明级别→张力标定错了，内核在放走真矛盾。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import 沙盘
from 饥内核_接口测试 import 饥内核, 标定

# conflict_type → 级别（外设报级别，尺度归内核）
级别映射 = {
    '结论冲突': '大事',   # 两条结论互相否定，最重
    '情境冲突': '中事',   # 同一主题两段对不上
    '粒度冲突': '小事',   # 长短不一样，不算真矛盾
}


def main():
    print('=== 沙盘 × 饥内核：用真实矛盾对测裁决 ===\n')
    entries = 沙盘.load_entries()
    pairs = 沙盘.find_pairs_dedup(entries, limit=8)
    print(f'活跃条目 {len(entries)} 条，独立矛盾源 {len(pairs)} 对\n')

    if not pairs:
        print('没有候选矛盾对（记忆库不够矛盾），无法测')
        return 1

    表 = []
    for p in pairs:
        a, b = 沙盘.by_id(entries, p['a']), 沙盘.by_id(entries, p['b'])
        if not a or not b:
            continue
        ct = p['conflict_type']
        级别 = 级别映射.get(ct, '中事')
        张力, 落差, 代价 = 标定(级别)
        指令, 分量 = 饥内核(张力, 落差, 代价)
        表.append({
            '对': f"{a['title'][:14] or a['id']} × {b['title'][:14] or b['id']}",
            '类型': ct, '级别': 级别, '压强': p['pressure'], '内核裁决': 指令,
            'A层': a['layer'], 'B层': b['layer'],
        })

    print(f"{'矛盾对':<34} {'类型':<8} {'级别':<6} {'压强':<5} {'内核裁决'}")
    print('-' * 70)
    for r in 表:
        print(f"{r['对']:<34} {r['类型']:<8} {r['级别']:<6} {r['压强']:<5} {r['内核裁决']}")

    # 可证伪判据
    结论冲突放走 = [r for r in 表 if r['类型'] == '结论冲突' and r['内核裁决'] == '消化']
    粒度冲突误判 = [r for r in 表 if r['类型'] == '粒度冲突' and r['内核裁决'] != '消化']
    print()
    if 结论冲突放走:
        print(f'⚠ {len(结论冲突放走)} 个结论冲突被判「消化」——内核正在放走真矛盾！')
    if 粒度冲突误判:
        print(f'⚠ {len(粒度冲突误判)} 个粒度冲突被判成需要处理——内核在给琐事加戏')
    if not 结论冲突放走 and not 粒度冲突误判:
        print('PASS——结论冲突≥中事（不放过），粒度冲突≤中事（不加戏）')
        print('   内核裁决与矛盾级别一致：真矛盾不逃，琐事不重')
    return 1 if 结论冲突放走 else 0


if __name__ == '__main__':
    sys.exit(main())
