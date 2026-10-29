# -*- coding: utf-8 -*-
"""平衡器.py —— ④ 平衡器：L 的「实际是 B」与 R 的「整体判断」是否指向同一件事

规格（逻辑最大化与饥关卡.md ④）：
  平衡 = L 的「实际是 B」 与 R 的「整体判断」是否指向同一件事
  同向 → 消化，饥降（降幅 = 压强 × 0.2）
  反向/无关 → 挂起，饥 = 压强全值，记「挂起原因」

做法：3B 判三分类 A=同向 B=反向 C=无关。解析失败 → 默认挂起（宁挂勿放）。

跑法：
  python 平衡器.py --test          # 用内置样例测
  from 平衡器 import judge         # judge(L, R) -> ('A'|'B'|'C', 理由)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

try:
    from 沙盘 import gen as _gen
except Exception:
    _gen = None

SYS = '''你是「平衡器」。拿到两段判断，判断它们是否指向同一件事。
只回答一个词：
是 = 两段话说的其实是同一回事（可以消化）
否 = 说的不是同一件事，或互相矛盾（要挂起）
格式：是/否 + 一句简短理由。'''

PROMPT = '''L 判断：「{l_actual}」
R 判断：「{r_whole}」

这两段判断说的是同一件事吗？回答 是/否。'''


def _clean(text, key):
    """从 L/R 输出里抽关键段（抽不到就用全文）"""
    m = re.search(key + r'[^。；;]*[。；;]', text)
    return m.group(0).strip() if m else text.strip()[:120]


STOP = set('''的 了 是 在 我 你 他 她 它 这 那 和 与 或 而 就 都 也 很 吗 呢 吧 啊
和 及 等 之 于 个 这 那 一些 什么 怎么 因为 所以 但是 不是 没有 可以 需要
实际 我以为 整体 这段 这句 那段 主题 内容 记录 判断 说的 是否 同一 件事'''.split())


def _keys(text):
    """中文 2-gram 关键词（去常见虚词/占位词），返回 set"""
    t = re.sub(r'[^\u4e00-\u9fa5]', '', text)
    grams = set()
    for i in range(len(t) - 1):
        g = t[i:i + 2]
        if g not in STOP and len(g) == 2:
            grams.add(g)
    return grams


def rule_judge(l_text, r_text):
    """机械判定：L 的「实际是」段 与 R 的「整体」段 共享关键词数"""
    ka = _keys(_clean(l_text, r'实际是'))
    kb = _keys(_clean(r_text, r'整体'))
    shared = ka & kb
    if len(shared) >= 2:
        return 'A', '共享关键词: %s' % '、'.join(sorted(shared)[:6]), len(shared)
    return 'C', '共享关键词不足: %s' % '、'.join(sorted(shared)[:6]), len(shared)


def judge(l_text, r_text, engine=None):
    w, why, n = rule_judge(l_text, r_text)
    if w == 'A':
        return w, why
    # 共享 1 个词时，可选模型二次判定（宁挂勿放）
    if n == 1 and engine is not None and _gen:
        l_actual = _clean(l_text, r'实际是')
        r_whole = _clean(r_text, r'整体')
        raw = _gen(PROMPT.format(l_actual=l_actual, r_whole=r_whole), SYS)
        if raw and '是' in raw:
            return 'A', '模型二次判定: ' + raw.strip()[:80]
    return 'C', why


def decide(l_text, r_text, 压强=1.0, engine=None):
    """返回 {'action': 消化|挂起, 'which': A/B/C, 'why': 理由, '饥变化': 值}"""
    which, why = judge(l_text, r_text, engine)
    if which == 'A':
        return {'action': '消化', 'which': which, 'why': why,
                '饥变化': round(压强 * 0.2, 2)}
    return {'action': '挂起', 'which': which, 'why': why, '饥变化': round(压强, 2)}


if __name__ == '__main__':
    if '--test' in sys.argv:
        L = '①解轴：错记的「他说全删是对的」与记录「别删」对不上。②对读：差在「说过」和「没说过」。③追源：我把「记忆记录」当成了「他实际说过的话」。④命题化：我以为他说过全删，实际是他从没说过全删这句；差在证据层；证据=原文指针；若原话核对一致则推翻我'
        R = '①情境：时间=2026-10-27，关系=讨论中，语气证据=原话「我也是够畜生的，去删了」。②整体：这段在解决「他说过全删」这个误会——他实际说的是别删。③原样：「去删了」'
        d = decide(L, R, 压强=1.5)
        print('L/R 样例 → 判定：%s（%s）理由：%s' % (d['action'], d['which'], d['why']))
        L2 = '①解轴：A。②对读：B。③追源：我把「X」当成「Y」。④命题化：我以为 X 实际 Y；差在证据层；证据=原文；若原文一致则推翻'
        R2 = '①情境：时间=2026-10-27，关系=闲聊，语气证据=原话「随便」。②整体：这段在聊天气。③原样：「随便」'
        d2 = decide(L2, R2, 压强=1.0)
        print('无关样例 → 判定：%s（%s）理由：%s' % (d2['action'], d2['which'], d2['why']))
    else:
        print('用法：python 平衡器.py --test')
