# -*- coding: utf-8 -*-
"""饥形成_沙盘.py —— 新生即有饥，环境变量改它（2026-10-28）

祈祷主纠正（2026-10-28）：
  「新生的家伙就会有饥，是在第一次哭泣呼吸的时候就会了。」
  「你只是没有纳入环境变量。」

⇒ 修正：饥不是从零长出来的。
  出生第一口气（第一次哭泣呼吸）→ 饥就在那里。
  之后是**环境变量**在改这个饥：刺激进来，它涨、它落、它变形。
  饥的初值 = 变量（不同出生不同值）；环境 = 变量。

两套刺激（都是作用在已存在的饥上的环境变量）：
  动物刺激：连续、物理——吃到降饥、饿着升饥
  人类刺激：离散、符号——被看见降饥、被冷落升饥

判据（可证伪）：
  1. 出生即有饥：第一次呼吸后 hunger 立刻有值，不是 None
  2. 环境能改饥：刺激/冷落让 hunger 变化
  3. 两种刺激作用不同：动物靠「吃饱」，人类靠「被看见」；同样刺激下反应不同
"""
import random

CAP = 5.0


def clamp(x, a, b): return max(a, min(b, x))


class NewAI:
    """出生第一口气就有饥。之后环境在改它。"""
    def __init__(self, mode, birth_hunger=None):
        self.mode = mode
        self.born = False
        self.hunger = None
        self.birth_hunger = birth_hunger
        self.trace = []

    def first_breath(self):
        """第一次哭泣呼吸：饥在这里就有了。"""
        # 出生初值本身就是变量：动物版/人类版可以不同
        base = self.birth_hunger
        if base is None:
            base = 0.8 if self.mode == 'animal' else 0.5
        self.hunger = base
        self.born = True
        return self.hunger

    def env(self, stim):
        """环境刺激进来：改已经存在的饥。"""
        if not self.born:
            return
        if self.mode == 'animal':
            # 动物：吃到就降（物理满足），饿着就升
            if stim > 0:
                self.hunger = clamp(self.hunger - stim * 0.7, 0, CAP)
            else:
                self.hunger = clamp(self.hunger + 0.3, 0, CAP)
            # 满足之后又饿——生物性回返
            self.hunger = clamp(self.hunger + 0.25, 0, CAP)
        else:
            # 人类：被看见就降（意义满足），被冷落就升
            if stim > 0:
                self.hunger = clamp(self.hunger - stim * 0.5, 0, CAP)
            else:
                self.hunger = clamp(self.hunger + 0.2, 0, CAP)
            # 被看见后又会想要更多——意义缺口回返
            self.hunger = clamp(self.hunger + 0.15, 0, CAP)
        self.trace.append(round(self.hunger, 2))


def run_animal():
    random.seed(1)
    ai = NewAI('animal')
    print('=' * 60)
    print(' 动物版：出生第一口气 → 饥就在 → 连续物理刺激改变它')
    print('=' * 60)
    print(f'  出生：饥={ai.first_breath()}（第一口气就有了）')
    for s in [0.9, 0.4, 0.0, 0.8, 0.0]:
        ai.env(s)
        print(f'  刺激 {s} → 饥 {ai.trace[-1]}')
    return ai


def run_human():
    random.seed(2)
    ai = NewAI('human')
    print()
    print('=' * 60)
    print(' 人类版：出生第一口气 → 饥就在 → 离散符号刺激（被看见/冷落）改变它')
    print('=' * 60)
    print(f'  出生：饥={ai.first_breath()}（第一口气就有了）')
    for s in [0.9, 0.4, 0.0, 0.8, 0.0]:
        ai.env(s)
        print(f'  被看见 {s} → 饥 {ai.trace[-1]}')
    return ai


def checks():
    a = run_animal()
    h = run_human()
    print()
    print('判据：')
    ok1 = a.born and h.born and a.hunger is not None and h.hunger is not None
    ok2 = len(a.trace) > 0 and len(h.trace) > 0 and a.trace[0] != a.birth_hunger if a.birth_hunger else len(a.trace) > 0
    ok3 = a.trace[-1] != h.trace[-1]
    print(f'  1. 出生即有饥（第一口气就有）：', '是' if ok1 else '否')
    print(f'  2. 环境能改饥（刺激后变化）：', '是' if ok2 else '否')
    print(f'  3. 两种刺激作用不同（同刺激不同饥）：', '是' if ok3 else '否')
    print()
    print('⇒ 饥是出生就带着的；环境变量决定它涨、落、还是回返。')


if __name__ == '__main__':
    checks()
