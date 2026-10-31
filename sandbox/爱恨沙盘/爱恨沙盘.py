# -*- coding: utf-8 -*-
"""培育_类我_v4.py —— 一块池、一个差值：差值低=爱，高=恨（不发布）
阿余 17:7x：「所有矛盾保持在一块位置，差值低了是爱，高了是恨。」
模型：矛盾只有一池；每 tick 量一个差值 D（池的积压×老化）；D 低于阈值 → 爱（多获取、轻触）；
D 高于阈值 → 恨（多解决、用力）。爱恨不是两套系统，是同一个差值的两端。
90 天 × 两世界 × 三个阈值，看谁活、爱恨各占多少。
"""
import random
from pathlib import Path

T = 2160
SEED = 20261031


class Agent:
    def __init__(self, name, theta, max_pool=20):
        self.name, self.theta, self.max_pool = name, theta, max_pool
        self.h = 0.30
        self.pool = []          # 唯一的位置：所有矛盾在一起 [[sev, age]]
        self.crashed = False
        self.love_ticks = self.hate_ticks = 0
        self.arrived_ext = self.acq = self.resolved = 0
        self.peak_pool = 0
        self.d_trace = []

    def tick(self, rng, lam):
        if self.crashed:
            return
        self.h = min(1.0, self.h + 0.002)
        if rng.random() < lam:
            self.pool.append([rng.uniform(0.2, 1.0), 0])
            self.arrived_ext += 1
        for b in self.pool:
            b[1] += 1
        D = sum(sev * min(1.0, age / 24) for sev, age in self.pool)
        self.d_trace.append(D)
        if D < self.theta:          # 差值低 = 爱：贴近、轻触、多获取
            self.love_ticks += 1
            for _ in range(2):
                self.pool.append([rng.uniform(0.2, 0.6), 0])
                self.acq += 1
                self.h = min(1.0, self.h + 0.002)
        else:                       # 差值高 = 恨：推开、用力、多解决
            self.hate_ticks += 1
            for _ in range(3):
                if not self.pool:
                    break
                self.pool.sort(key=lambda x: x[0] * x[1], reverse=True)
                if rng.random() < 0.8:
                    self.pool.pop(0)
                    self.resolved += 1
                self.h = min(1.0, self.h + 0.005)
        if self.h > 0.60:
            self.h = 0.30
        self.peak_pool = max(self.peak_pool, len(self.pool))
        if len(self.pool) > self.max_pool:
            self.crashed = True


def run(lam_fn):
    rng = random.Random(SEED)
    agents = [Agent("θ=0.5（易恨）", 0.5), Agent("θ=0.8", 0.8), Agent("θ=1.2（易爱）", 1.2)]
    for t in range(T):
        for a in agents:
            a.tick(rng, lam_fn(t))
    return agents


def calm(t):
    return 0.15


def bursty(t):
    return 1.2 if (t % 24) >= 12 else 0.10


rows = []
for name, fn in [("A 平静", calm), ("B 突发", bursty)]:
    for a in run(fn):
        n = len(a.d_trace)
        rows.append(dict(世界=name, 名字=a.name, 崩='是' if a.crashed else '否',
                         峰池=a.peak_pool, 平均D=round(sum(a.d_trace) / n, 2),
                         爱占比=round(a.love_ticks / n, 2), 恨占比=round(a.hate_ticks / n, 2),
                         外部=a.arrived_ext, 获取=a.acq, 解决=a.resolved))

lines = ["# 爱恨沙盘：一块池 · 一个差值 · 爱/恨", "",
         "| 世界 | 名字 | 崩 | 峰池 | 平均D | 爱占比 | 恨占比 | 外部 | 获取 | 解决 |",
         "|---|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    lines.append(f"| {r['世界']} | {r['名字']} | {r['崩']} | {r['峰池']} | {r['平均D']} | "
                 f"{r['爱占比']} | {r['恨占比']} | {r['外部']} | {r['获取']} | {r['解决']} |")
lines += ["", "## 判", "",
          "1. 一个池、一个差值：矛盾不分堆；D 低（贴近）=爱（轻触、获取），D 高（推远）=恨（用力、解决）。",
          "2. θ 是爱恨的分界：θ 低易恨（多解决、少获取，渴求淡），θ 高易爱（多获取、解决慢，容易积压）。",
          "3. 平静/突发两世界都不崩的 θ，就是「差值调得住」的那个点。"]
out = Path(__file__).with_name("数据_爱恨沙盘.md")
out.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
print(f"\n>> {out}")
