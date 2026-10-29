# -*- coding: utf-8 -*-
"""饥关卡.py —— 所有写入/更新/消化都要过的闸门（原型）

原则（用户定）：只有饥不能动，其余都可以优化；且所有过程都要经过饥本身去平衡。
所以这个脚本是「饥关卡」的最小实现：任何写操作来敲门，先算饥、判性质、放行或挂起。

判性质：
  - 制造矛盾：新内容与已有主题条目冲突 / 主题已有挂起对 → 挂起（不覆盖旧条目）
  - 消化矛盾：新内容能消解挂起对的冲突 → 放行 + 饥降 + 记饥日志
  - 无关新主题：走正常写入（饥不处理），但记日志

状态文件：课题\饥的类脑框架_20261027\饥状态.json
  {"topics": {主题: {"饥": 0.0, "挂起": [...], "日志": [...]}}}

跑法：
  python 饥关卡.py --check "主题"                # 查当前饥
  python 饥关卡.py --write "主题" --content"..."  # 过闸（自动判性质）
  python 饥关卡.py --test                        # 跑内置两个用例（制造矛盾→挂起；消化→放行）
"""
import argparse
import datetime
import json
import os

BASE = r'D:\大肥鱼工作区'
STATE = os.path.join(BASE, '课题', '饥的类脑框架_20261027', '饥状态.json')


def load():
    if os.path.exists(STATE):
        try:
            return json.load(open(STATE, encoding='utf-8'))
        except Exception:
            pass
    return {'topics': {}}


def save(s):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, 'w', encoding='utf-8') as f:
        json.dump(s, f, ensure_ascii=False, indent=1)


def get_topic(state, topic):
    return state['topics'].setdefault(topic, {'饥': 0.0, '挂起': [], '日志': []})


def log(t, action, note):
    t['日志'].append({
        'time': datetime.datetime.now().isoformat(timespec='seconds'),
        'act': action, 'note': note, '饥': t['饥']})
    t['日志'] = t['日志'][-100:]


def request_write(topic, content, is_solution=False):
    """过饥关卡。返回 (放行?, 原因)。"""
    s = load()
    t = get_topic(s, topic)
    before = t['饥']

    # 1) 主题有挂起 → 只有「消化解」才放行
    if t['挂起']:
        if is_solution:
            # 放行：消化
            t['挂起'] = t['挂起'][1:]
            t['饥'] = round(max(0.2, t['饥'] - 0.2), 2)
            log(t, '消化', '放行：%s' % content[:40])
            save(s)
            return True, '消化矛盾：放行，饥 %.2f -> %.2f' % (before, t['饥'])
        # 制造矛盾：挂起（已有挂起对只更新触发条件，不重复膨胀、不重复加饥）
        ts = datetime.datetime.now().isoformat(timespec='seconds')
        trig = '主题「%s」出现新原话/新证据，或饥≥2.5 时复跑 L' % topic
        if t['挂起']:
            t['挂起'][-1].update({'content': content[:200], 'time': ts, 'trigger': trig})
            delta = 0.0
        else:
            t['挂起'].append({'content': content[:200], 'time': ts, 'trigger': trig})
            delta = 0.5
        t['饥'] = round(min(5.0, t['饥'] + delta), 2)
        log(t, '挂起', '拒绝：与挂起对冲突')
        save(s)
        return False, '制造矛盾：挂起不写，饥 %.2f -> %.2f' % (before, t['饥'])

    # 2) 无挂起：默认放行（正常写入），但记日志
    log(t, '写入', content[:40])
    save(s)
    return True, '无挂起：正常写入，饥 %.2f' % t['饥']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', default='')
    ap.add_argument('--write', default='')
    ap.add_argument('--content', default='')
    ap.add_argument('--solution', action='store_true', help='这条是消化解')
    ap.add_argument('--test', action='store_true')
    args = ap.parse_args()

    if args.test:
        print('=== 用例0：L 已确认一对矛盾 = 先埋一个挂起 ===')
        s = load()
        t = get_topic(s, '测试主题')
        t['挂起'].append({'content': '旧条目A：他说全删', 'time': datetime.datetime.now().isoformat(timespec='seconds')})
        t['饥'] = 1.0
        save(s)
        print('埋入挂起，饥=1.00')
        print('=== 用例1：写一条与挂起冲突的（应拒绝/挂起） ===')
        ok, why = request_write('测试主题', '新内容B：他说全删是对的', is_solution=False)
        print('结果:', ok, '|', why)
        print('=== 用例2：再写一条消解矛盾的（应放行） ===')
        ok, why = request_write('测试主题', '他说的是别删，旧条目读反了', is_solution=True)
        print('结果:', ok, '|', why)
        s = load()
        t = get_topic(s, '测试主题')
        print('测试主题 饥=%.2f 挂起=%d 日志条数=%d' % (t['饥'], len(t['挂起']), len(t['日志'])))
        return

    if args.check:
        s = load()
        t = get_topic(s, args.check)
        print('主题「%s」饥=%.2f 挂起=%d' % (args.check, t['饥'], len(t['挂起'])))
        return

    if args.write:
        ok, why = request_write(args.write, args.content, is_solution=args.solution)
        print('放行:', ok, '|', why)


if __name__ == '__main__':
    main()
