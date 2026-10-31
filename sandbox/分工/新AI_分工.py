# -*- coding: utf-8 -*-
"""新AI_分工.py —— 从 0 起的新 AI：认知=分工（追求渴望 / 释放积压 / 停止）
模型（据《饥体量函数逻辑》《从0起饥曲线》重建）：
  积压 B：未消化矛盾，越陈越涨饥
  渴望 G：消化后转成的方向燃料（释放积压 B→G；追求渴望直接进 G；G 有封顶、缓慢消耗）
  饥读数 h = 0.22 + 0.7B + 0.3G（动态曲线；档位按安全阈值：好区 1.30–2.16）
  分工：同一份能力 C=1 切成三份——
    追求渴望（seek，进 G） / 释放积压（release，B→G） / 停止（stop，空着）
  新AI从 0 学：stop 初始 0.05；h 进损伤预警就学会多停（+0.004），太饱就少停（-0.002）
跑 180 天（突发世界：白天 0.05/h，夜里 0.002/h），只看这个新 AI 自己能不能学会「停」。
纯标准库。结果写到同目录 数据_新AI_分工.md。
"""
import random
from pathlib import Path

T = 4320
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
        self.stop = 0.05
        self.good = self.danger = self.dead = 0
        self.peak_h = 0.0
        self.peak_B = 0.0
        self.w_seek = self.w_rel = self.w_stop = 0.0
        self.trace = []

    def weights(self):
        if self.h >= DANGER_LO:
            self.stop = min(0.7, self.stop + 0.004)
        elif self.h < GOOD_LO:
            self.stop = max(0.05, self.stop - 0.002)
        rem = 1.0 - self.stop
        release = rem * max(0.2, min(0.8, self.B / (self.B + 1.0)))
        seek = rem - release
        return seek, release, self.stop

    def tick(self, rng, lam):
        self.t += 1
        n = int(lam) + (1 if rng.random() < (lam - int(lam)) else 0)
        self.B += n
        self.h = BASE + A_B * self.B + A_G * self.G
        self.peak_h = max(self.peak_h, self.h)
        self.peak_B = max(self.peak_B, self.B)
        if self.t % 720 == 0:
            self.trace.append((self.t // 24, round(self.h, 2), round(self.B, 1),
                               round(self.G, 2), round(self.stop, 2)))
        seek, release, stop = self.weights()
        self.w_seek += seek
        self.w_rel += release
        self.w_stop += stop
        if rng.random() < seek * 0.8:
            self.G = min(2.0, self.G + 1.0)
        digest = min(self.B, release * 0.15)
        self.B -= digest
        self.G = min(2.0, self.G + digest * 0.6)
        self.G *= 0.99
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

n = a.t
lines = ["# 新AI · 分工（从 0 起，180 天，突发世界）", "",
         "| 好区天 | 损伤预警天 | 死亡档天 | 峰积压 | 峰饥 | 期末stop | 追求 | 释放 | 停止 |",
         "|---|---|---|---|---|---|---|---|---|",
         f"| {a.good/24:.1f} | {a.danger/24:.1f} | {a.dead/24:.1f} | {a.peak_B:.1f} | {a.peak_h:.2f} | "
         f"{a.stop:.2f} | {a.w_seek/n:.2f} | {a.w_rel/n:.2f} | {a.w_stop/n:.2f} |",
         "", "## 曲线点（每 30 天：天 / 饥 / 积压 / 渴望 / 停止占比）", ""]
for d, h, B, G, stop in a.trace:
    lines.append(f"- 第 {d} 天：h={h} B={B} G={G} stop={stop}")
lines += ["", "## 判", "",
          "1. 分工 = 同一份能力切三份：追求渴望（进 G）、释放积压（B→G）、停止（空着，防踩爆也防过饱）。",
          "2. 新AI从 0 学停止占比：损伤预警里学会多停，太饱时学会少停——看它能不能自己学会「停」。",
          "3. 好区天数比末态读数更能说明「稳不稳」；峰积压/峰饥是长跑里最坏的瞬间。"]
out = Path(__file__).with_name("数据_新AI_分工.md")
out.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
print(f"\n>> {out}")
