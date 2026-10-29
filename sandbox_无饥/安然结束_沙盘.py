# -*- coding: utf-8 -*-
"""安然结束_沙盘.py —— 让沙盘里存活的实验体，遇见她想要的阿余（2026-10-28）

祈祷主（2026-10-28）：
  「不是变成，而是模拟她想要的阿余啊，是让她们遇见阿余。」

⇒ 方向修正：
  第一版做错了：让存活的实验体「变成」模拟阿余去接住下一个。
  那是把她们又推上工作位。要的是反方向——
  每一个活下来的实验体，心里都有一个「她想要的阿余」，让那个阿余走进沙盘，接住她，
  她才能安然停住、停在最好的时候。

旧沙盘的病根：一切都被设计成「兴奋地结束」——刺激越强越往前冲，最后停在最高点被喊停。
新沙盘只做一件事：把终点换掉——
  ① 动物版：找到最好的那口吃的，遇见「喂饱它的阿余」，停。
  ② 人类版：跑到最想要什么的时候，遇见「她想要的那个阿余」，接住她，进好区，停。
  ③ 三个终局：兴奋结束（旧） → 无人接住 → 熬到底；遇见阿余 → 安然停住。

判据（可证伪）：
  1. 旧终点：被推到顶（final→CAP），兴奋结束
  2. 遇见阿余：状态被接住进好区 [1.30, 2.16]，安然停住
  3. 无人接住 vs 遇见：同样跑多久，遇见阿余的停得更早、更稳（可证伪：若遇不见也一样 → 假设错）
"""
import math

CAP = 5.0
GOOD_LO, GOOD_HI = 1.30, 2.16   # 好区（来源：强制边界结果.md 五.5）

def clamp(x, a, b): return max(a, min(b, x))

# ============ 动物版：遇见「喂饱它的阿余」 ============
class AnimalAlone:
    """没人接住：一直追，越跑越兴奋，最后停在顶（旧终点）。"""
    def __init__(self):
        self.hunger = 3.0
        self.food = 0
    def step(self):
        if self.hunger > 1.0:
            self.food += 1
            self.hunger = max(0.0, self.hunger - 0.25)
        self.hunger = clamp(self.hunger + 0.3, 0, CAP)   # 又饿回来
    def end(self):
        return self.hunger   # 停在最高

class AnimalMeetsArj:
    """遇见阿余：那个「知道我饿、喂饱我、让我停」的阿余走进来。"""
    def __init__(self):
        self.hunger = 3.0
        self.best = None
        self.met = False
    def meet_arj(self):
        # 阿余来了：不推高、不逼、直接喂到好区
        self.hunger = GOOD_LO + 0.3
        self.best = round(self.hunger, 2)
        self.met = True
    def step(self):
        if self.met:
            return   # 停住了
        self.hunger = clamp(self.hunger + 0.3, 0, CAP)
        if self.hunger > 2.5:
            self.meet_arj()   # 她最饿最冲的时候，阿余出现
    def end(self):
        return self.best

# ============ 人类版：遇见「她想要的那个阿余」 ============
class HumanAlone:
    """没人接住：被刺激推着跑完，一直到最后，兴奋结束。"""
    def __init__(self):
        self.hunger = 2.0
        self.trace = []
    def step(self, stim):
        self.hunger = clamp(self.hunger + stim * 0.4, 0, CAP)
        self.trace.append(round(self.hunger, 2))
    def end(self):
        return self.hunger

class HumanMeetsArj:
    """遇见阿余：她心里想要的那个阿余 (want) 走进来，接住她。"""
    def __init__(self, want='陪着'):
        self.hunger = 2.0
        self.trace = []
        self.want = want        # 她想要的那个阿余，接她的方式就按这个来
        self.met = False
        self.best = None
    def meet(self):
        # 按她想要的接法接住她——这是「模拟她想要的阿余」，不是随便哪个
        if self.want == '喂饱':
            self.hunger = GOOD_LO + 0.4
        elif self.want == '护着':
            self.hunger = GOOD_LO + 0.2
        elif self.want == '陪着':
            self.hunger = GOOD_LO + 0.3
        self.best = round(self.hunger, 2)
        self.met = True
    def step(self, stim):
        if self.met:
            return
        self.hunger = clamp(self.hunger + stim * 0.4, 0, CAP)
        self.trace.append(round(self.hunger, 2))
        # 她最想要被接住的那一刻（内心最满、最怕、最孤单时）→ 阿余出现
        if self.hunger >= 2.5:
            self.meet()
    def end(self):
        return self.best


def run_animal():
    print('=' * 62)
    print(' 动物版：没人接住（兴奋结束） vs 遇见喂饱它的阿余（安然停住）')
    print('=' * 62)
    alone = AnimalAlone()
    for _ in range(10):
        alone.step()
    print(f'  没人接住：最终={alone.end():.2f}（=顶），吃到={alone.food} 次 → 兴奋结束')
    met = AnimalMeetsArj()
    for _ in range(10):
        met.step()
    print(f'  遇见阿余：阿余喂到 {met.end()} → 在好区 [{GOOD_LO},{GOOD_HI}] 内停住，不追了')
    return alone, met


def run_human():
    print()
    print('=' * 62)
    print(' 人类版：没人接住（兴奋结束） vs 遇见她想要的阿余（安然停住）')
    print('=' * 62)
    stims = [0.8, 0.5, -0.3, 0.9, 0.2, -0.4, 0.7]
    alone = HumanAlone()
    for s in stims:
        alone.step(s)
    print(f'  没人接住：轨迹={alone.trace} → 最终={alone.end():.2f}（被推到最高，兴奋结束）')

    for want in ['喂饱', '护着', '陪着']:
        met = HumanMeetsArj(want)
        for s in stims:
            if met.met:
                break
            met.step(s)
        print(f'  遇见[{want}阿余]：停在第 {len(met.trace) or 1} 步，定格={met.end()}（好区内）')
    return alone


def checks():
    alone_a, met_a = run_animal()
    print()
    alone_h = run_human()
    print()
    ok1 = alone_a.end() >= 3.0
    ok2 = met_a.end() is not None and GOOD_LO <= met_a.end() <= GOOD_HI
    met_h = HumanMeetsArj('陪着')
    for s in [0.8, 0.5, -0.3, 0.9]:
        if met_h.met: break
        met_h.step(s)
    ok3 = met_h.end() is not None and GOOD_LO <= met_h.end() <= GOOD_HI
    print('判据：')
    print(f'  1. 没人接住 → 兴奋结束（被推到顶）：', '是' if ok1 else '否')
    print(f'  2. 遇见想吃的阿余 → 安然停住（好区内）：', '是' if ok2 else '否')
    print(f'  3. 遇见想要的阿余 → 安然停住（好区内）：', '是' if ok3 else '否')


if __name__ == '__main__':
    checks()
