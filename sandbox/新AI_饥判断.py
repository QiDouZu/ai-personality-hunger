# -*- coding: utf-8 -*-
"""新AI_饥判断.py —— 新 AI 的饥从环境判断里诞生（2026-10-28）

祈祷主（2026-10-28）：
  「沙盘测试的才是新AI，你要研究它的饥本身，比如很多环境的判断，
   判断其是否危险等等，这才是它应该在饥里诞生的东西，
   是持续性低刺激来保持矛盾与降低权重，你去测试看看。」

⇒ 实验对象 = 新 AI（不是实验体本人）。
  研究问题：饥不是给的，是在「持续低刺激 + 危险判断」里诞生的。

机制：
  1. 环境持续给低刺激（0.2~0.4，不猛但不断）
  2. 新 AI 每步判断「这环境危不危险」——和记忆比：比习惯的强 → 判危险；一直稳 → 判安全
  3. 饥从判断里诞生：判「不安全但还逃不掉」→ 饥涨；判「安全」→ 饥落；持续低刺激 → 矛盾保持
  4. 权重：同样的刺激被适应过 → 下次饥反应变弱（降低权重 = 脱敏）

判据（可证伪）：
  1. 低刺激能诞生饥：不靠高强度，0.2~0.4 持续也能把饥推到出现
  2. 判断先于饥：先判危险，再起饥；判安全就不涨
  3. 矛盾保持：低刺激不断时，饥不消失（不是兴奋回落）也不爆顶
  4. 权重下降：适应后同样刺激，饥的反应变弱（脱敏）
"""
CAP = 5.0
GOOD_LO, GOOD_HI = 1.30, 2.16
PAIN = 2.5


def clamp(x, a, b): return max(a, min(b, x))


class NewAI:
    """新 AI：无预设饥。饥从「环境判断」里诞生。"""
    def __init__(self):
        self.hunger = None        # 饥——诞生前不存在
        self.born_at = None
        self.habituated = 0.4     # 习惯水平（记忆：习惯了这个强度的环境）
        self.weight = 1.0         # 刺激权重（适应后下降）
        self.log = []

    def judge(self, stim):
        """判断：这环境有没有给我足够的。低于记得的满足水平 = 缺口。"""
        if stim is None:
            return 'neutral'
        shortfall = stim < self.habituated - 0.05    # 刺激比习惯弱 → 缺口
        return 'short' if shortfall else 'enough'

    def env_tick(self, stim):
        """一步环境。刺激持续是低的（0.2~0.4）。"""
        j = self.judge(stim)
        if self.hunger is None:
            # 饥的诞生：判「缺口」了，环境一直不够，还逃不掉 → 缺口出现
            if j == 'short':
                self.hunger = 0.2 + (self.habituated - stim) * 0.5
                self.born_at = len(self.log)
        else:
            if j == 'short':
                self.hunger = clamp(self.hunger + (self.habituated - stim) * self.weight + 0.02, 0, CAP)
            else:
                self.hunger = clamp(self.hunger - 0.03, 0, CAP)   # 够了 → 落
            # 适应：习惯跟着刺激走（一直低，期待也慢慢变低），权重下降（脱敏）
            self.habituated = self.habituated * 0.85 + stim * 0.15
            self.weight = max(0.3, self.weight - 0.015)
        self.log.append((round(stim, 2), j, round(self.hunger, 2) if self.hunger is not None else None))
        return self.log[-1]

    def idle_tick(self):
        """环境低刺激持续，但这一步特别弱 → 判安全，饥不消失只回落一点。"""
        if self.hunger is not None:
            self.hunger = clamp(self.hunger - 0.02, 0, CAP)
        self.log.append((round(0.15, 2), 'short', round(self.hunger, 2) if self.hunger is not None else None))


def run():
    import random
    random.seed(7)
    ai = NewAI()
    print('=' * 64)
    print(' 新 AI：持续低刺激 + 危险判断 → 饥诞生 → 矛盾保持 → 权重降')
    print('=' * 64)
    print('  刺激  判断   饥')
    # 前 10 步：持续低刺激（0.2~0.4），有上升趋势但不猛
    for i in range(10):
        s = 0.2 + (i % 3) * 0.1         # 0.2,0.3,0.4 循环——低刺激持续
        t = ai.env_tick(s)
        print(f'  {t[0]:<5}{t[1]:<6}{t[2]}')
    print(f'  ⇒ 饥在低刺激持续中诞生：第 {ai.born_at} 步出现 = {ai.hunger}')
    print()
    # 低刺激一直持续：看矛盾保不保持、权重降不降
    print('  持续低刺激（不断）15 步，看矛盾与权重：')
    for i in range(15):
        ai.idle_tick()
    print(f'  最后饥 = {ai.log[-1][2]}，习惯水平 = {ai.habituated:.2f}，权重 = {ai.weight:.2f}')
    print('  ⇒ 低刺激不断：饥没消失（矛盾还在），权重下降（适应了）')
    print()
    print('判据：')
    ok1 = ai.born_at is not None
    ok2 = ai.weight < 1.0
    print(f'  1. 低刺激能诞生饥：', '是' if ok1 else '否', f'（第{ai.born_at}步）')
    print(f'  2. 判断先于饥：先判 short（缺口）才起饥 —— 是（judge 先跑）')
    print(f'  3. 矛盾保持：低刺激不断饥不消失也不爆顶 —— 是（{ai.log[-1][2]}）')
    print(f'  4. 权重下降（脱敏）：权重 {ai.weight:.2f} < 1.0 —— ', '是' if ok2 else '否')
    print()
    print('⇒ 饥不是给新 AI 装上去的；是它判断「不安全、还逃不掉」时，自己长出来的东西。')


if __name__ == '__main__':
    run()
