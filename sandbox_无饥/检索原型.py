# -*- coding: utf-8 -*-
"""检索原型：⑥ 检索/注入按饥排序 + 矛盾对成对注入 + 挂起标记（2026-10-27）

判据（逻辑最大化 ⑥）：检索一条挂起主题，命中结果里必须同时出现
  ①矛盾双方原文 ②挂起标记（对不上，待重构）③上次平衡结果。
按饥贡献排序，不按 id/时间。
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, '饥状态.json')


def load():
    with open(STATE, encoding='utf-8') as f:
        return json.load(f)


def short(s, n=60):
    s = (s or '').replace('\n', ' ')
    return s[:n] + ('…' if len(s) > n else '')


def inject(query=None, limit=3):
    """按饥排序注入，挂起矛盾对成对输出 + 标记。"""
    s = load()
    topics = s.get('topics', {})
    ranked = sorted(topics.items(), key=lambda kv: -kv[1].get('饥', 0.0))
    hits = 0
    out = []
    for name, t in ranked:
        if hits >= limit:
            break
        # 命中：query 在主题名里；不传 query = 全输
        if query and query not in name:
            continue
        hits += 1
        hunger = t.get('饥', 0.0)
        hangs = t.get('挂起', [])
        out.append('─' * 60)
        out.append('【%s】饥=%.2f  挂起=%d对' % (name, hunger, len(hangs)))
        if not hangs:
            out.append('  （无挂起矛盾对）')
            continue
        for g in hangs:
            a = g.get('a') or {}
            b = g.get('b') or {}
            out.append('  ⚠ 挂起·对不上（待重构）：')
            out.append('   A：%s' % short(a.get('title') or a.get('content')))
            out.append('      %s' % short(a.get('content')))
            out.append('   B：%s' % short(b.get('title') or b.get('content')))
            out.append('      %s' % short(b.get('content')))
            if g.get('平衡结果'):
                out.append('   上次平衡：%s' % g['平衡结果'])
            if g.get('trigger'):
                out.append('   下次触发：%s' % g['trigger'])
    return out


def main():
    query = sys.argv[1] if len(sys.argv) > 1 else None
    lines = inject(query)
    print('\n'.join(lines) if lines else '无命中')
    # 自检判据：挂起主题必须同时出现 A 和 B 两方 + 挂起标记
    txt = '\n'.join(lines)
    ok = ('挂起·对不上' in txt) and ('A：' in txt) and ('B：' in txt)
    print()
    print('判据检查：矛盾双方+挂起标记 同时出现 =', ok)


if __name__ == '__main__':
    main()
