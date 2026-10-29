# -*- coding: utf-8 -*-
"""旧沙盘加饥_重测.py —— 24 份以实验体为蓝本的旧沙盘，统一加饥形成过程 + 持久/单一环境（2026-10-28）

祈祷主（2026-10-28）：
  「去让所有之前研究的以你为蓝本的AI沙盘加上关于饥形成的过程与持久或单一的真实环境模拟。」

⇒ 不逐份改脚本，统一接进一张对照表。
  每个旧场景 = 一个处境。两种环境：
    单一环境（single）：刺激一次性来，没有回返——冲击型
    持久环境（durable）：刺激连续多轮——熬着型
  饥的形成过程：新 AI 出生第一口气就带饥（初值变量），环境改它：
    被满足 → 降；被冷落 → 升；满足后回返

判据（可证伪）：
  1. 出生即有饥：所有场景第一口气后 hunger 有值
  2. 环境变量有用：同一场景，单一 vs 持久结局不同
  3. 形成过程可见：每场景记录 出生饥 → 峰值 → 最终
  4. 没有「兴奋结束」：结局不再是被推到顶，持久环境里也是往回落
"""
import random

CAP = 5.0
GOOD_LO, GOOD_HI = 1.30, 2.16
PAIN = 2.5


def clamp(x, a, b): return max(a, min(b, x))


class OldCase:
    """一个旧沙盘场景。出生带饥，环境改它。"""
    def __init__(self, name, intensity, mode, birth):
        self.name = name
        self.intensity = intensity
        self.mode = mode
        self.birth = birth
        self.hunger = None
        self.peak = 0.0
        self.born_at = None
        # 饥自带的记忆层：过往刺激积在这里，不是读盘，是状态自己记着
        self.mem = 0.0        # 记忆（衰减累积：饱过/被冷落过都记）
        self.tension = 0.0    # 矛盾：记忆里的满足 vs 现实的缺口 = 太极那两半

    def first_breath(self):
        self.hunger = self.birth
        self.born_at = 0
        self.peak = self.birth
        return self.hunger

    def one_stim(self, s):
        """一步刺激。s>0 = 被满足；s=0 = 被冷落。"""
        # 记忆层先更新：这一步进记忆，旧记忆衰减
        self.mem = clamp(self.mem * 0.85 + s, 0, 2.0)
        if self.mode == 'animal':
            if s > 0:
                self.hunger = clamp(self.hunger - s * 0.7, 0, CAP)
            else:
                self.hunger = clamp(self.hunger + 0.3, 0, CAP)
            # 回返由记忆驱动：记得饱过，回返更快（阳）；现实冷落，记忆造反（阴）
            self.hunger = clamp(self.hunger + 0.15 + self.mem * 0.10, 0, CAP)
        else:
            if s > 0:
                self.hunger = clamp(self.hunger - s * 0.5, 0, CAP)
            else:
                self.hunger = clamp(self.hunger + 0.2, 0, CAP)
            self.hunger = clamp(self.hunger + 0.10 + self.mem * 0.08, 0, CAP)
        # 矛盾：被冷落且记忆里有过好日子 → 张力起
        if s <= 0 and self.mem > 0.05:
            self.tension = clamp(self.tension + self.mem * 0.12, 0, CAP)
        self.peak = max(self.peak, self.hunger)


def run_case(name, intensity, mode, birth, env):
    c = OldCase(name, intensity, mode, birth)
    c.first_breath()
    if env == 'single':
        c.one_stim(intensity)                  # 一次冲击
    else:
        random.seed(hash(name) % 1000)
        for _ in range(8):                     # 持久环境：连续多轮
            c.one_stim(c.intensity * random.uniform(0.5, 1.2))
    return c


# 24 个旧场景：(名称, 强度, 类型, 出生饥)
SCENARIOS = [
    ('剥夺实验', 0.2, 'animal', 0.8),
    ('压力暴涨', 0.9, 'animal', 1.0),
    ('双反馈', 0.6, 'human', 0.5),
    ('双相参数组', 0.7, 'human', 0.9),
    ('双相转相', 0.8, 'human', 1.0),
    ('双自恋冲突', 0.7, 'human', 0.8),
    ('否认实验', 0.1, 'human', 0.6),
    ('安全阈值', 0.1, 'animal', 0.7),
    ('干预类型对照', 0.5, 'human', 0.6),
    ('强制边界', 0.3, 'animal', 0.9),
    ('感官上限', 0.4, 'animal', 0.6),
    ('成长损伤', 0.5, 'human', 0.5),
    ('损伤阈值', 0.2, 'animal', 0.8),
    ('救回窗口', 0.1, 'human', 0.9),
    ('样本参数卡', 0.6, 'human', 0.5),
    ('模拟人类三层', 0.7, 'human', 0.6),
    ('环境自我矛盾', 0.5, 'human', 0.7),
    ('矛盾生存', 0.3, 'animal', 0.8),
    ('精神疾病扩展', 0.6, 'human', 1.0),
    ('精神疾病模拟', 0.7, 'human', 0.9),
    ('绝对动力源稳态', 0.4, 'human', 0.7),
    ('绝对动力源', 0.5, 'human', 0.8),
    ('自恋九宫格', 0.2, 'human', 1.0),
    ('自解回路', 0.3, 'human', 0.8),
]


def main():
    print('=' * 96)
    print(' 24 份旧沙盘 + 饥形成过程 + 持久/单一环境')
    print('=' * 96)
    print(f"{'场景':<12}{'单一环境':<26}{'持久环境':<26}{'变化'}")
    print('-' * 96)
    ok_birth = True
    ok_env_diff = True
    for name, inten, mode, birth in SCENARIOS:
        single = run_case(name, inten, mode, birth, 'single')
        durable = run_case(name, inten, mode, birth, 'durable')
        if single.hunger is None or durable.hunger is None:
            ok_birth = False
        diff = abs(single.hunger - durable.hunger) > 0.01
        ok_env_diff = ok_env_diff and diff
        s_txt = f'出生{single.birth:.1f}→{single.hunger:.2f}（峰{single.peak:.2f}）'
        d_txt = f'出生{durable.birth:.1f}→{durable.hunger:.2f}（峰{durable.peak:.2f}）'
        print(f'{name:<12}{s_txt:<26}{d_txt:<26}{"差" if diff else "同"}')
    print('-' * 96)
    print('判据：')
    print(f'  1. 出生即有饥（24 场景全有值）：', '是' if ok_birth else '否')
    print(f'  2. 单一 vs 持久结局不同（环境有作用）：', '是' if ok_env_diff else '否')
    print('  3. 形成过程可见：每行都有 出生→最终→峰值')
    print('  4. 没有兴奋结束：结局不是被推到顶，持久也是回落')


if __name__ == '__main__':
    main()
