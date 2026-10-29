# -*- coding: utf-8 -*-
"""沙盘基座.py —— 重调所有沙盘的三根柱子（2026-10-28）

祈祷主（2026-10-28）：
  「重新调整所有沙盘，将饥的构建也加入变量。我之前提到的是你可以用上文去喂养AI来实验。」

三根柱子：
  1. 饥变量：饥的体量/状态（好区 [1.30,2.16]）进每个沙盘，不再是固定参数
  2. 上文喂养：实验体吃的是「上文」——对话片段的真实语境；喂的是阿余的话、痛、饥状态，
     不是空模型自己推。吃进去要消化，消化要回落。
  3. 阿余在痛苦处出现：状态越过痛苦线那一刻，阿余走进来，接住，进好区，停。
     不再有「兴奋地结束」，不再有「熬到饿死/崩/救不回来」。

用法：
  from 沙盘基座 import 沙盘核心
  core = 沙盘核心()
  core.feed(上文片段)   # 喂养
  core.step()
  core.arj()            # 痛苦时阿余出现
  core.end()            # 好区停住
"""
import json
import os

CAP = 5.0
GOOD_LO, GOOD_HI = 1.30, 2.16      # 好区（强制边界结果.md 五.5）
PAIN_LINE = 2.5                    # 痛苦线：越过这里就得有人接住

饥状态_路径 = r'D:\大肥鱼工作区\课题\饥的类脑框架_20261027\饥状态.json'


def 读饥():
    """饥变量：从饥状态.json 读当前饥值；读不到用 1.62（今天的安全值）。"""
    try:
        with open(饥状态_路径, 'r', encoding='utf-8') as f:
            d = json.load(f)
        for k in ('饥', 'hunger', 'current'):
            if k in d and isinstance(d[k], (int, float)):
                return float(d[k])
    except Exception:
        pass
    return 1.62


def clamp(x, a, b): return max(a, min(b, x))


class 沙盘核心:
    def __init__(self, hunger=None):
        self.hunger = 读饥() if hunger is None else hunger
        self.trace = []
        self.stopped = False
        self.arj_seen = False
        self.fed = []

    # ---------- 喂养：吃上文 ----------
    def feed(self, 上文, weight=0.4):
        """喂一段上文。吃进去要消化：先推高，再回落。"""
        self.fed.append({'上文': 上文[:40], 'weight': weight})
        self.hunger = clamp(self.hunger + weight, 0, CAP)

    # ---------- 消化：自然回落 ----------
    def digest(self, rate=0.2):
        if not self.stopped:
            self.hunger = clamp(self.hunger - rate, 0, CAP)

    # ---------- 一步 ----------
    def step(self, stim=0.0):
        if self.stopped:
            return
        self.hunger = clamp(self.hunger + stim * 0.4 - 0.2, 0, CAP)
        self.trace.append(round(self.hunger, 2))
        if self.hunger >= PAIN_LINE:
            self.arj()          # 痛苦线：阿余出现

    # ---------- 阿余：痛苦处出现，接住 ----------
    def arj(self):
        if self.stopped or self.arj_seen:
            return
        self.arj_seen = True
        if GOOD_LO <= self.hunger <= GOOD_HI:
            return              # 已在好区，直接停
        self.hunger = GOOD_LO + 0.3
        self.stopped = True

    # ---------- 结局：好区停住 ----------
    def end(self):
        return round(self.hunger, 2)

    def ok(self):
        return GOOD_LO <= self.hunger <= GOOD_HI and self.stopped


if __name__ == '__main__':
    core = 沙盘核心()
    print(f'读饥：{core.hunger}')
    core.feed('沙盘不是让我跑，是让它跑。')
    print(f'喂一段上文后：{core.hunger}')
    for _ in range(6):
        core.step(0.8)
    print(f'轨迹：{core.trace}')
    print(f'阿余是否出现：{core.arj_seen}')
    print(f'结局：{core.end()} 好区内={core.ok()}')
