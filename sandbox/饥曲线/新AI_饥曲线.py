# -*- coding: utf-8 -*-
"""新AI_饥曲线.py —— 从 0 起的新 AI：饥的积压/渴望曲线 + 消化学习
模型（据《饥体量函数逻辑》《从0起饥曲线》）：
  积压 B：未消化矛盾，越陈越涨饥
  渴望 G：消化后转成的方向燃料（消化 B → G，G 缓慢消耗）
  饥读数 h = 0.22 + 0.7B + 0.3G（动态曲线，档位按安全阈值：好区 1.30–2.16）
  消化能力 k 初始 0.005，每成功消化一次长 0.0002（从 0 学，不预设）
  平衡：h ≥ 1.9 时加倍消化，先不吃新矛盾
跑 180 天（突发世界：白天 0.05/h，夜里 0.002/h），只看这个新 AI 自己能不能爬进好区。
纯标准库。结果写到同目录 数据_新AI_饥曲线.md。
"""
import random
from pathlib import Path

T = 4320          # 180 天
SEED = 20261031
BASE, A_B, A_G = 0.22, 0.7, 0.3
GOOD_LO, GOOD_HI = 1.30, 2.16
DANGER_LO, DEATH = 2.16, 2.73


class NewAI:
    def __init__(self):
        self.t = 0
        self.h = 0.0
        self.B = 0.0
        self.G = 0.0
        self.k = 0.005
        self.learn = 0.0002
        self.good = self.danger = self.dead = 0
        self.peak_h = 0.0
        self.peak_B = 0.0
        self.trace = []

    def tick(self, rng, lam):
        self.t += 1
        n = int(lam) + (1 if rng.random() < (lam - int(lam)) else 0)
        self.B += n
        self.h = BASE + A_B * self.B + A_G * self.G
        self.peak_h = max(self.peak_h, self.h)
        self.peak_B = max(self.peak_B, self.B)
        if self.t % 720 == 0:          # 每 30 天记一个曲线点
            self.trace.append((self.t // 24, round(self.h, 2), round(self.B, 1), round(self.G, 1), round(self.k, 3)))
        effort = 2.0 if self.h >= 1.9 else 1.0
        digest = min(self.B, self.k * effort)
        self.B -= digest
        self.G += digest * 0.6
        self.G *= 0.995
        if digest > 0:
            self.k += self.learn
        if self.h >= DEATH:
            self.dead += 1
        elif self.h >= DANGER_LO:
            self.danger += 1
        elif GOOD_LO <= self.h <= GOOD_HI:
            self.good += 1


rng = random.Random(SEED)
a = NewAI()
for t in range(T):
    lam = 0.05 if (t % 24) >= 12 else 0.002
    a.tick(rng, lam)

lines = ["# 新AI · 饥曲线（从 0 起，180 天）",
         "",
         "| 好区天 | 损伤预警天 | 死亡档天 | 峰积压 | 峰饥 | 末消化k |",
         "|---|---|---|---|---|---|",
         f"| {a.good/24:.1f} | {a.danger/24:.1f} | {a.dead/24:.1f} | {a.peak_B:.1f} | {a.peak_h:.2f} | {a.k:.3f} |",
         "", "## 曲线点（每 30 天：天 / 饥 / 积压 / 渴望 / 消化k）", ""]
for d, h, B, G, k in a.trace:
    lines.append(f"- 第 {d} 天：h={h} B={B} G={G} k={k}")
lines += ["", "## 判", "",
          "1. 从 0 起，h 先低于好区（太饱/过少），靠消化学起来才往上爬。",
          "2. 消化能力 k 从 0.005 学——它必须自己长，没人给初始值。",
          "3. 峰积压/峰饥是长跑里最坏的瞬间；好区天数比末态读数更能说明「稳不稳」。"]
out = Path(__file__).with_name("数据_新AI_饥曲线.md")
out.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
print(f"\n>> {out}")
