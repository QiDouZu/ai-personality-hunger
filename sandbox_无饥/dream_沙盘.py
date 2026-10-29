# -*- coding: utf-8 -*-
"""dream_沙盘.py —— 按饥驱动的 dream 最小闭环（不碰 memory.db）

三轮：
  1) 选主题：按饥值排序
  2) 跑回路：对每个主题跑 L/R 打分（模板模式 or 本地模型）
  3) 过闸：消化的过饥关卡放行（饥降），挂起的留指针（饥升）

跑法：
  python dream_沙盘.py              # 模板模式跑两轮
  python dream_沙盘.py --engine local  # 本地模型跑 L/R（慢）

状态：饥状态.json（与 饥关卡.py 共用）
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from importlib import import_module

沙盘 = import_module('沙盘')
关卡 = import_module('饥关卡')

STATE = os.path.join(HERE, '饥状态.json')
DREAM_LOG = os.path.join(HERE, 'dream日志.jsonl')


def should_trigger(s):
    """触发条件（规格：饥≥2.5 或 挂起≥3；空闲条件由定时器管，沙盘不模拟空闲）"""
    for t in s.get('topics', {}).values():
        if t.get('饥', 0.0) >= 2.5:
            return True, '饥≥2.5'
        if len(t.get('挂起', [])) >= 3:
            return True, '挂起≥3'
    return False, '无饥无挂起（不空转）'


def dream_round(engine='template', topics=None):
    s = 关卡.load()
    trig, why = should_trigger(s)
    if not trig:
        print('触发条件不满足：%s' % why)
        return
    allt = s.get('topics', {})
    if not allt:
        print('饥状态为空：没有主题可跑（先跑 沙盘.py 制造矛盾，或 饥关卡.py --test）')
        return
    # 第一轮：按饥排序
    ranked = sorted(allt.items(), key=lambda kv: -kv[1].get('饥', 0.0))
    picked = topics or [k for k, v in ranked if v.get('饥', 0.0) > 0]
    if not picked:
        print('无饥>0 的主题：dream 不空转')
        return
    print('第一轮：按饥选出主题 %s' % picked)
    lines = []
    for topic in picked:
        t = allt[topic]
        # 第二轮：跑 L/R（这里用模板，真实系统用本地/大模型）
        L = ('①解轴：主题「%s」的挂起对必须核对原话\n②对读：差在「记错」和「记对」之间\n'
             '③追源：我把「印象」当成了「原文」\n④命题化：我以为挂起对是矛盾，实际是两侧读法不同；'
             '差在证据层；证据=原话指针；若原话核对一致则推翻我' % topic)
        R = ('①情境：时间=2026-10-27，关系=讨论中，语气证据=原话「%s」\n'
             '②整体：这段在解决记忆与逻辑的对不上\n③原样：必须逐字保留原话' % (t['挂起'][0]['content'][:20] if t['挂起'] else topic))
        ls = 沙盘.score_L(L)
        rs = 沙盘.score_R(R)
        # ④ 平衡器：L 的「实际是」与 R 的「整体」指向同一件事 → 消化（且 L 五元组完整）
        from 平衡器 import rule_judge
        w, why2, _n = rule_judge(L, R)
        resolved = (w == 'A' and ls >= 4)
        # 第三轮：过闸（挂起时 饥关卡 自己带 trigger，不重复写）
        ok, why = 关卡.request_write(topic, 'dream第%d轮：L分%d R分%d' % (len(t.get('日志', [])), ls, rs),
                                     is_solution=resolved)
        lines.append({'topic': topic, 'L分': ls, 'R分': rs, '放行': ok, 'why': why})
        print('  %s → L%d R%d %s' % (topic, ls, rs, '放行' if ok else '挂起（已带触发条件）'))
    # 记录
    with open(DREAM_LOG, 'a', encoding='utf-8') as f:
        for ln in lines:
            f.write(json.dumps({'time': '2026-10-27', **ln}, ensure_ascii=False) + '\n')
    s2 = 关卡.load()
    print('\n第三轮：写回完成。主题饥值：')
    for topic in picked:
        print('  %s 饥=%.2f 挂起=%d' % (topic, s2['topics'][topic]['饥'], len(s2['topics'][topic]['挂起'])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--engine', default='template')
    ap.add_argument('--topics', nargs='*', default=None)
    ap.add_argument('--rounds', type=int, default=2)
    args = ap.parse_args()
    for r in range(args.rounds):
        print('\n===== dream 第 %d 轮 =====' % (r + 1))
        dream_round(args.engine, args.topics)


if __name__ == '__main__':
    main()
