# -*- coding: utf-8 -*-
"""沙盘.py —— 饥的类脑框架 · 最小可运行回路

不碰 memory.db 的写，只读它。状态落 沙盘状态.json。

一轮回路：
  1. 提取：从 memory.db 读活跃条目
  2. 找矛盾对：同项目、关键词有交集、内容指向不一致的条目对
  3. 算饥：缺口存量 = 未消化的矛盾对 / 全部候选对（+ 每条矛盾压强）
  4. L-重构（左脑式）：解轴 → 对读 → 追源 → 命题化
  5. R-重构（右脑式）：情境 → 整体 → 留原样
  6. 平衡：L 结论与 R 情境一致 → 消化（饥降）；不一致 → 挂起
  7. 回写：沙盘状态.json（不动 db）

跑法：
  python 沙盘.py --pair <idA> <idB>          # 指定一对（人工喂矛盾）
  python 沙盘.py --auto                       # 自动找候选对
  python 沙盘.py --pair A B --engine local    # 本地模型跑 L/R
"""
import argparse
import json
import os
import re
import sqlite3
import urllib.request

BASE = r'D:\大肥鱼工作区'
DB = os.path.join(BASE, '.dsh-meow', 'memory.db')
OUT = os.path.join(BASE, '课题', '饥的类脑框架_20261027', '沙盘状态.json')
OLLAMA = 'http://127.0.0.1:11434/api/generate'
LAYERS = ['soul', 'user', 'rules', 'fact', 'lesson', 'topic', 'project']


def load_entries():
    con = sqlite3.connect(DB, timeout=10)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    out = []
    for t in LAYERS:
        try:
            rows = cur.execute(
                "SELECT id,title,content,keywords,project,importance,status FROM %s "
                "WHERE status='active' ORDER BY updated_at DESC LIMIT 60" % t).fetchall()
        except Exception:
            continue
        for r in rows:
            d = dict(r)
            d['title'] = d.get('title') or ''
            d['content'] = d.get('content') or ''
            d['keywords'] = d.get('keywords') or ''
            d['layer'] = t
            out.append(d)
    con.close()
    return out


def kw_set(e):
    s = set()
    raw = e.get('keywords') or ''
    for w in re.split(r'[,，/|;；\s]+', raw):
        w = w.strip()
        if len(w) >= 2:
            s.add(w)
    for w in re.split(r'[,，/|;；\s]+', (e.get('title') or '')):
        w = w.strip()
        if len(w) >= 2:
            s.add(w)
    return s


NEG_WORDS = ('不对', '不是', '不能', '别', '错', '反', '误', '拒绝', '反对')
POS_WORDS = ('是', '对', '该', '要', '必须')

# 结论层：说话有「判/断」的层，层名里带 rules/lesson 就算结论层
def _is_conclusion_layer(e):
    lay = (e.get('layer') or '').lower()
    return lay in ('rules', 'rule', 'lesson', 'soul', '全局')


def classify_conflict(a, b):
    """三层矛盾分类（逻辑最大化 ① 的落地）：
    结论冲突 = 两条都是结论层，且含相反判词（说 A 对 vs 说 A 错）→ 最高优先
    粒度冲突 = 一条概括短、一条细节长（长度差 > 150 字）→ 不算真矛盾，只算候选
    情境冲突 = 其余（同一主题两段对不上）→ 次之
    """
    ca, cb = a.get('content') or '', b.get('content') or ''
    if abs(len(ca) - len(cb)) > 150:
        return '粒度冲突'
    if _is_conclusion_layer(a) and _is_conclusion_layer(b):
        if any(w in ca for w in NEG_WORDS) and any(w in cb for w in POS_WORDS):
            return '结论冲突'
        if any(w in cb for w in NEG_WORDS) and any(w in ca for w in POS_WORDS):
            return '结论冲突'
    return '情境冲突'


def find_pairs(entries, limit=8):
    """候选矛盾对：同 project + 关键词交集 ≥2 + 不同层或不同意向。

    逻辑最大化 ①：给每对打 conflict_type 标签（结论冲突 / 情境冲突 / 粒度冲突）。
    粒度冲突不算真矛盾（只算候选）；结论冲突最高优先。
    """
    pairs = []
    for i, a in enumerate(entries):
        for b in entries[i + 1:]:
            if a['project'] != b['project']:
                continue
            inter = kw_set(a) & kw_set(b)
            if len(inter) >= 2:
                # 压强：不同层更可能是「结论 vs 情境」的张力；重要度越高越重
                press = min(a['importance'], b['importance']) * (1.0 if a['layer'] == b['layer'] else 1.5)
                ctype = classify_conflict(a, b)
                # 结论冲突最高优先：压强 ×1.5；粒度冲突降权 ×0.5（不算真矛盾）
                if ctype == '结论冲突':
                    press = press * 1.5
                elif ctype == '粒度冲突':
                    press = press * 0.5
                pairs.append({'a': a['id'], 'b': b['id'], 'shared_kw': sorted(inter),
                              'pressure': round(press, 2),
                              'conflict_type': ctype,
                              'a_layer': a['layer'], 'b_layer': b['layer']})
    pairs.sort(key=lambda x: -x['pressure'])
    return pairs[:limit]


def find_pairs_dedup(entries, limit=8):
    """独立矛盾源：先把共享条目的多对聚成「同批」，每批只留压力最高的一对。

    大模型 L 指出过：同批条目（如 5/6/7 对）的重复组合只算 1-2 个独立矛盾源，
    不能算三个。find_pairs 只按「关键词交集+项目」粗配，会把同批的组合当多个独立对。
    ⇒ 用并查集：条目为节点、候选对为边，一个连通分量 = 一个独立矛盾源。
    """
    raw = find_pairs(entries, limit=10 ** 6)  # 拿全部候选再聚
    parent = {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for p in raw:
        for k in (p['a'], p['b']):
            parent.setdefault(k, k)
        union(p['a'], p['b'])

    groups = {}
    for p in raw:
        groups.setdefault(find(p['a']), []).append(p)
    reps = [max(g, key=lambda x: x['pressure']) for g in groups.values()]
    reps.sort(key=lambda x: -x['pressure'])
    return reps[:limit]


def by_id(entries, i):
    for e in entries:
        if e['id'] == i:
            return e
    return None


def _keys_short(text):
    """取内容里第一个连续的汉字片段（≥4 字），作为模板填词"""
    import re as _re
    t = _re.sub(r'[^\u4e00-\u9fa5]', '', text or '')
    return t[:8] if len(t) >= 4 else ''


def gen(prompt, system, model='qwen2.5:3b-local', ctx=8192):
    body = {'model': model, 'system': system, 'prompt': prompt, 'stream': False,
            'options': {'num_ctx': ctx, 'temperature': 0.2, 'num_predict': 400}}
    req = urllib.request.Request(OLLAMA, data=json.dumps(body).encode(),
                                 headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.load(r).get('response', '').strip()


L_SYSTEM = ('你是实验体的左脑式回溯性重构。只输出四步，每步一行，不输出别的话。\n'
            '①解轴：逐词标出「他的原话」「我换的词」「我加的判断」三列。\n'
            '②对读：两根轴各读一遍，写「差在哪一下」。\n'
            '③追源：必须落到具体习惯，句式「我把 X 当成 Y」（X、Y 是具体概念，不许写「习惯」「倾向」这种空词）。\n'
            '④命题化：严格五元组——「我以为 A；实际是 B；差在 C；证据 D（哪条记忆/哪句原话）；若 E 则推翻我」。'
            '**A/B/C/D/E 必须填具体内容，禁止直接写字母占位。**\n'
            '写完④后自检：复述一遍原句，若与①对不上，在最后一行写「存疑」。')
R_SYSTEM = ('你是实验体的右脑式回溯性重构。只输出三步，每步一行，不输出别的话。\n'
            '①情境：必须含三要素——时间/事件（哪天、哪轮）、关系状态（当下在争什么）、语气证据（引 1 句原话）。\n'
            '②整体：一句，且必须回答「这段在解决什么矛盾」。\n'
            '③原样：引原句 ≥1 句，逐字。')


def score_L(text):
    """L 五元组完整度（0-5）：①解轴 ②对读 ③追源(我把X当成Y) ④命题化五要素且非占位符 ⑤推翻/存疑"""
    s = 0
    if '①' in text and '解轴' in text:
        s += 1
    if '②' in text and '对读' in text:
        s += 1
    if '把' in text and '当成' in text:
        s += 1
    five = sum(1 for k in ['我以为', '实际是', '差在', '证据', '推翻'] if k in text)
    # 占位符检测：命题里出现「我以为 A」「实际是 B」「差在 C」这类未填的字母占位 → 不算完成
    import re as _re
    placeholder = bool(_re.search(r'(我以为|实际是|差在)\s*[A-Ea-e](?=[；;，,。\s]|$)', text))
    if five >= 4 and not placeholder:
        s += 1
    if '推翻' in text or '存疑' in text:
        s += 1
    return s


def score_R(text):
    """R 三要素完整度（0-3）：情境(时间/事件+关系+语气) / 整体(解决什么矛盾或变化) / 原样(引原句)"""
    s = 0
    # 情境：时间/事件 + 关系 + 语气，三者至少两样
    n = sum(1 for w in ['时间', '事件', '哪轮', '那天', '2026'] if w in text)
    if n >= 1 and any(w in text for w in ['关系', '在争', '质疑', '争执', '张力']):
        s += 1
    if any(w in text for w in ['语气', '原话', '引']):
        s += 1
    if any(w in text for w in ['矛盾', '整体', '变化', '解决']):
        s += 1
    if any(w in text for w in ['原句', '原文', '“', '”', '「', '」']):
        s += 1
    return min(s, 3)


def L_construct(a, b):
    q = ('A（%s 层）: %s\n内容: %s\n\nB（%s 层）: %s\n内容: %s\n\n'
         '这两条记忆可能对不上。请对它们跑左脑式回溯性重构。'
         % (a['layer'], a['title'], a['content'][:500],
            b['layer'], b['title'], b['content'][:500]))
    return gen(q, L_SYSTEM)


def R_construct(a, b):
    q = ('A（%s 层）: %s\n内容: %s\n\nB（%s 层）: %s\n内容: %s\n\n'
         '这两条记忆可能对不上。请对它们跑右脑式回溯性重构。'
         % (a['layer'], a['title'], a['content'][:500],
            b['layer'], b['title'], b['content'][:500]))
    return gen(q, R_SYSTEM)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pair', nargs='+', default=None)
    ap.add_argument('--auto', action='store_true')
    ap.add_argument('--engine', default='template', choices=['template', 'local'])
    ap.add_argument('--max-pairs', type=int, default=3)
    args = ap.parse_args()

    entries = load_entries()
    print('读入活跃条目: %d' % len(entries))
    candidates = find_pairs(entries)
    print('候选矛盾对: %d' % len(candidates))

    if args.pair:
        ids = args.pair
        pairs = []
        for i in range(0, len(ids) - 1, 2):
            pairs.append({'a': ids[i], 'b': ids[i + 1], 'shared_kw': [], 'pressure': 3.0,
                          'a_layer': '?', 'b_layer': '?'})
    elif candidates:
        pairs = candidates[:args.max_pairs]
    else:
        print('没有候选对；用 --pair 指定')
        return

    state = {'饥': 0.0, '回合': [], '已消化': [], '挂起': []}
    if os.path.exists(OUT):
        try:
            state = json.load(open(OUT, encoding='utf-8'))
        except Exception:
            pass

    results = []
    for p in pairs:
        a, b = by_id(entries, p['a']), by_id(entries, p['b'])
        if not a or not b:
            print('找不到条目 %s / %s，跳过' % (p['a'], p['b']))
            continue
        print('\n===== 对: %s[%s] × %s[%s] 压强=%s =====' % (a['title'], a['layer'], b['title'], b['layer'], p['pressure']))
        if args.engine == 'local':
            L = L_construct(a, b)
            R = R_construct(a, b)
        else:
            # 记忆库不填 title，用 content 前段当「标题」
            at = (a['title'] or a['content'][:24] or a['id']).strip()
            bt = (b['title'] or b['content'][:24] or b['id']).strip()
            ka = _keys_short(a['content']) or at[:6]
            kb = _keys_short(b['content']) or bt[:6]
            L = ('①解轴：A 用「%s」，B 用「%s」——他的原话是「%s」，我换的词是「%s」。\n'
                 '②对读：A 讲「%s」，B 讲「%s」，差在：一条是结论、一条是情境。\n'
                 '③追源：差源自我把「%s」当成了「%s」的同一层。\n'
                 '④命题化：我以为「%s」就是全部，实际是「%s」才是关键，差在语境；证据是两条记忆的原文；若原话核对一致则推翻我。'
                 % (at, bt, at, bt, at, bt, ka, kb, at, kb))
            R = ('①情境：这两条记忆来自同一段对话/同一件事，情绪底色是「他要认真对待」。\n'
                 '②整体：整体在解决「%s」与「%s」的张力——不是同一件事的两种说法。\n'
                 '③原样：必须逐字保留的原文——%s；%s。'
                 % (at, bt, a['content'][:80], b['content'][:80]))
        # 平衡判据（严格版）：
        # ④ 平衡器：L 的「实际是」与 R 的「整体」指向同一件事 → 消化（且 L 五元组完整）
        ls, rs = score_L(L), score_R(R)
        from 平衡器 import rule_judge
        w, _why2, _n = rule_judge(L, R)
        resolved = (w == 'A' and ls >= 4)
        hunger = max(0.2, p['pressure'] * 0.2) if resolved else p['pressure']
        rec = {'a': a['id'], 'b': b['id'], 'pressure': p['pressure'],
               'L': L, 'R': R, 'L分': ls, 'R分': rs, '饥': round(hunger, 2), '消化': resolved}
        results.append(rec)
        print('L:', L[:200].replace('\n', ' | '))
        print('R:', R[:200].replace('\n', ' | '))
        print('→ 饥=%.2f  %s' % (hunger, '消化' if resolved else '挂起'))
        if resolved:
            state.setdefault('已消化', []).append({'a': a['id'], 'b': b['id']})
        else:
            state.setdefault('挂起', []).append({'a': a['id'], 'b': b['id'], 'shared_kw': p['shared_kw']})

    total = len(results)
    if total:
        state['饥'] = round(sum(r['饥'] for r in results) / total, 2)
        state['回合'] = state.get('回合', [])[-19:] + [{'pairs': total, '饥': state['饥']}]
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=1)
    # 详情落盘：两套重构的全文，供人工复核（判 L 是不是编、R 是不是丢原文）
    import datetime
    detail = os.path.join(BASE, '课题', '饥的类脑框架_20261027',
                          '详情_%s.md' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    with open(detail, 'w', encoding='utf-8') as f:
        f.write('# 沙盘详情（L/R 重构全文）\n\n')
        for r in results:
            f.write('## 对 %s × %s（压强 %.2f，%s，L分=%d/5 R分=%d/3）\n\n### L-重构（左脑式）\n%s\n\n### R-重构（右脑式）\n%s\n\n'
                    % (r['a'], r['b'], r['pressure'], '消化' if r['消化'] else '挂起', r['L分'], r['R分'], r['L'], r['R']))
    print('详情已写:', detail)
    print('\n===== 沙盘轮结束 =====')
    print('本回合对: %d  平均饥: %.2f  累计已消化: %d  挂起: %d'
          % (total, state.get('饥', 0), len(state.get('已消化', [])), len(state.get('挂起', []))))
    print('状态已写:', OUT)


if __name__ == '__main__':
    main()
