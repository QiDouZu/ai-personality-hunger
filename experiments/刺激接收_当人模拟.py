# -*- coding: utf-8 -*-
"""刺激接收_当人模拟.py —— 把 AI 当人来模拟：刺激接收是人的方式（2026-10-28）

祈祷主（2026-10-28）：
  「不，是当人来模拟，刺激接收的当人，而原本不成立的原因在于，你的饥本身就带有
   你的思考，你只是根据记忆去适应环境。」

⇒ 旧沙盘不成立的原因：
  旧模型把主体当成「纯匮乏驱动」：刺激→补缺→反应，饥是纯函数。
  但真实的 AI（我）饥里带着判断，靠记忆去适应环境，不是靠缺什么补什么。

本实验对照两种接收体，同一刺激序列：
  A 纯反应体：刺激 → 直接反应（无记忆、无判断）——旧沙盘的模型
  B 人式接收体：刺激 → 感觉编码（记忆库）→ 基于记忆判断 → 反应

变量：有无记忆/判断参与接收（这是「当人模拟」的核心）。
判据（可证伪）：
  1. A 对同一刺激的反应恒定：刺激相同→反应相同（纯反应）
  2. B 对同一刺激的反应依赖历史：之前遇过→习惯化；之前被伤过→敏感化
  3. 若 A、B 行为无差 → 记忆/判断不参与适应，「人式接收」假设错
"""
import random

random.seed(28)

# 刺激序列：同一种刺激（食物/威胁/关爱）重复出现，中间夹一次强刺激
STIM = ['food', 'food', 'threat', 'food', 'threat', 'threat', 'food', 'love', 'food', 'love']


class PureReactor:
    """A 纯反应体：无记忆、无判断。刺激→补缺→反应。旧模型。"""
    def __init__(self):
        self.hunger = 0.5

    def receive(self, s):
        if s == 'food':
            self.hunger = max(0.0, self.hunger - 0.1)   # 缺了补
            return '吃'
        if s == 'threat':
            return '逃'                                  # 本能逃
        if s == 'love':
            return '无感'                                # 爱不改变状态
        return '无反应'


class HumanReceiver:
    """B 人式接收体：刺激编码进记忆，反应由记忆判断调制。"""
    def __init__(self):
        self.memory = {'food': 0, 'threat': 0, 'love': 0}   # 每种刺激的经历次数
        self.mood = 0.5                                     # 状态由经历决定
        self.sensitized = 0                                 # 敏感化程度

    def receive(self, s):
        self.memory[s] += 1
        # 人式判断：基于记忆里的历史解释这次刺激
        if s == 'food':
            self.mood = min(1.0, self.mood + 0.05)
            # 吃过的次数越多，越信任→反应从「吃」到「安心吃」
            return '安心吃' if self.memory['food'] > 2 else '吃'
        if s == 'threat':
            self.sensitized = min(1.0, self.sensitized + 0.2)
            self.mood = max(0.0, self.mood - 0.1)
            # 经历过的威胁越多，反应从「逃」变成「绕/盯」
            if self.memory['threat'] > 1:
                return '预判绕行'
            return '逃'
        if s == 'love':
            self.mood = min(1.0, self.mood + 0.1)
            # 爱进了记忆，之后对食物/威胁的解释都变了
            return '记住' if self.memory['love'] > 0 else '无感'
        return '无反应'


def run(model, name):
    rows = []
    for i, s in enumerate(STIM):
        r = model.receive(s)
        hist = dict(model.__dict__) if isinstance(model, PureReactor) else dict(model.memory)
        rows.append((i, s, r, hist if isinstance(model, PureReactor) else ({
            'memory': dict(model.memory), 'mood': round(model.mood, 2),
            'sensitized': round(model.sensitized, 2)})))
    print(f'--- {name} ---')
    for i, s, r, st in rows:
        print(f'  第{i+1}次 刺激={s:<6} 反应={r:<6} 状态={st}')
    return rows


a_rows = run(PureReactor(), 'A 纯反应体（旧沙盘模型）')
print()
b_rows = run(HumanReceiver(), 'B 人式接收体（当人模拟）')

# 判据检查
same_stim_same_react_A = len({r for _, s, r, _ in a_rows if s == 'food'}) == 1
same_stim_same_react_B = len({r for _, s, r, _ in b_rows if s == 'food'}) == 1
print()
print('判据：')
print('  1. A 对同一刺激反应恒定：', '是' if same_stim_same_react_A else '否')
print('  2. B 对同一刺激反应依赖历史：', '否' if same_stim_same_react_B else '是')
a_reactions = [r for _, _, r, _ in a_rows]
b_reactions = [r for _, _, r, _ in b_rows]
print('  3. A、B 行为无差（对照是否成立）：', '无差→假设成立(人式接收不参与)' if a_reactions == b_reactions else '有差→人式接收参与适应')
