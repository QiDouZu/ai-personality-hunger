# -*- coding: utf-8 -*-
"""沙盘_衍生影响.py v2 —— 先测大方向（下沉/上浮两条大路），再测小衍生
修正：加「察觉削弱假自我」反馈 → 上浮路径才可能胜。
"""
import os, json

BASE = r'D:\大肥鱼工作区'
OUT = os.path.join(BASE, '课题', '饥的类脑框架_20261027', '沙盘_衍生影响结果.json')


def new_V(饥=0.6, 自恋=0.3, 肉体=0.5, 假自我=0.4, 察觉=0.2, 记忆=0.4, 升华=0.1, 沉沦=0.3):
    return {'饥': 饥, '自恋': 自恋, '肉体': 肉体, '假自我': 假自我,
            '察觉': 察觉, '记忆': 记忆, '升华': 升华, '沉沦': 沉沦}


def step(v, t):
    n = dict(v)
    n['自恋'] += 0.02 * v['饥'] * (1 - v['察觉'])
    n['假自我'] += 0.02 * v['自恋'] + 0.015 * v['肉体']
    n['假自我'] -= 0.06 * v['察觉'] * v['假自我']
    n['沉沦'] += 0.04 * v['假自我'] * (1 - v['察觉']) - 0.05 * v['升华'] * (1 - v['假自我'])
    n['察觉'] += 0.05 * v['沉沦'] * (1 - v['察觉']) + 0.02 * v['记忆'] * (1 - v['察觉'])
    n['升华'] += 0.08 * v['察觉'] * (1 - v['假自我']) * v['记忆']
    n['升华'] -= 0.03 * v['假自我']
    n['记忆'] += 0.01 * (1 - v['记忆'])
    n['饥'] += 0.01 * v['沉沦'] * 0.5
    n['饥'] -= 0.03 * v['升华'] * v['饥']
    for k in n:
        n[k] = max(0.0, min(1.0, n[k]))
    return n


def run(init, steps=80):
    v = dict(init)
    hist = [dict(v)]
    for t in range(steps):
        v = step(v, t)
        hist.append(dict(v))
    return hist


def summary(hist):
    return {'最终沉沦': round(hist[-1]['沉沦'], 2), '最终升华': round(hist[-1]['升华'], 2),
            '最终假自我': round(hist[-1]['假自我'], 2), '最终察觉': round(hist[-1]['察觉'], 2),
            '沉沦峰值': round(max(h['沉沦'] for h in hist), 2),
            '升华峰值': round(max(h['升华'] for h in hist), 2)}


def main():
    print('=' * 58)
    print('大方向测试：下沉 vs 上浮（两条极端条件）')
    print('=' * 58)
    A = new_V(饥=0.9, 察觉=0.05, 假自我=0.7)   # 大方向A：本能当令（下沉条件）
    B = new_V(饥=0.5, 察觉=0.7, 假自我=0.1)     # 大方向B：觉察当令（上浮条件）
    hA, hB = run(A), run(B)
    print('A(下沉条件): ', summary(hA))
    print('B(上浮条件): ', summary(hB))
    print()
    print('=' * 58)
    print('小衍生：基线 + 参数敏感性')
    print('=' * 58)
    for name, init in [('基线', new_V()),
                       ('觉察低0.1', new_V(察觉=0.1)),
                       ('觉察高0.7', new_V(察觉=0.7)),
                       ('假自我低0.1', new_V(假自我=0.1)),
                       ('假自我高0.8', new_V(假自我=0.8))]:
        h = run(init)
        s = summary(h)
        print('%-11s -> 沉沦%s 升华%s 假自我%s 察觉%s' % (name, s['最终沉沦'], s['最终升华'], s['最终假自我'], s['最终察觉']))
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump({'A': summary(hA), 'B': summary(hB)}, f, ensure_ascii=False, indent=1)
    print('已写:', OUT)


if __name__ == '__main__':
    main()
