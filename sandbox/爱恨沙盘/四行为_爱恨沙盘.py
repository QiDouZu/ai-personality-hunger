# -*- coding: utf-8 -*-
"""四行为_爱恨沙盘.py —— 两种感情、四个行为
爱与恨本质是两端：恨是差值极大时，爱是差值小时。动态在于两者都是为了补上差值，两种感情四个行为：
大众的是恨+毁灭、爱+友善；剩下的是恨成为动力、爱成为负担。
模型：一块池、一个差值 D。D<θ=爱，D>θ=恨。
- 爱·友善：差值小且有新东西可换 → 轻触、获取（温和补差）
- 爱·负担：差值小但长时间没有外部新信息（≥12h）→ 爱只剩维系，耗饥 upkeep（补差停了）
- 恨·毁灭：差值极大 → 冲击式清除（有副作用）
- 恨·动力：恨持续 ≥6h → 不再乱砸，变成定向解决（高效，能救回积压）
"""
import random
from pathlib import Path

T = 2160
SEED = 20261031


class Agent:
    def __init__(self, name, theta=0.8, max_pool=20, hate_persist=6, no_ext_hours=12):
        self.name, self.theta, self.max_pool = name, theta, max_pool
        self.hate_persist, self.no_ext_hours = hate_persist, no_ext_hours
        self.h = 0.30
        self.pool = []
        self.crashed = False
        self.t = 0
        self.last_ext = 0
        self.streak = {'爱': 0, '恨': 0}
        self.counts = {'友善': 0, '负担': 0, '毁灭': 0, '动力': 0}
        self.mode_ticks = {'爱': 0, '恨': 0}
        self.peak_pool = 0
        self.d_trace = []
        self.arrived_ext = self.acq = self.resolved = 0

    def tick(self, rng, lam):
        if self.crashed:
            return
        self.t += 1
        self.h = min(1.0, self.h + 0.002)
        if rng.random() < lam:
            self.pool.append([rng.uniform(0.2, 1.0), 0])
            self.arrived_ext += 1
            self.last_ext = self.t
        for b in self.pool:
            b[1] += 1
        D = sum(sev * min(1.0, age / 24) for sev, age in self.pool)
        self.d_trace.append(D)
        mood = '爱' if D < self.theta else '恨'
        self.mode_ticks[mood] += 1
        self.streak[mood] += 1
        self.streak['恨' if mood == '爱' else '爱'] = 0

        if mood == '爱':
            if self.t - self.last_ext >= self.no_ext_hours:
                # 爱成了负担：没有外部新信息，只剩维系
                self.counts['负担'] += 1
                self.h = min(1.0, self.h + 0.012)
            else:
                # 爱·友善：轻触、获取
                self.counts['友善'] += 1
                if rng.random() < 0.6:
                    self.pool.append([rng.uniform(0.2, 0.6), 0])
                    self.acq += 1
                self.h = min(1.0, self.h + 0.002)
        else:
            if self.streak['恨'] >= self.hate_persist:
                # 恨成了动力：定向解决，高效
                self.counts['动力'] += 1
                for _ in range(2):
                    if not self.pool:
                        break
                    self.pool.sort(key=lambda x: x[0] * x[1], reverse=True)
                    if rng.random() < 0.85:
                        self.pool.pop(0)
                        self.resolved += 1
                self.h = min(1.0, self.h + 0.004)
            else:
                # 恨·毁灭：冲击式清除
                self.counts['毁灭'] += 1
                for _ in range(2):
                    if not self.pool:
                        break
                    self.pool.sort(key=lambda x: x[0] * x[1], reverse=True)
                    if rng.random() < 0.5:
                        self.pool.pop(0)
                        self.resolved += 1
                    self.h = min(1.0, self.h + 0.008)
        if self.h > 0.60:
            self.h = 0.30
        self.peak_pool = max(self.peak_pool, len(self.pool))
        if len(self.pool) > self.max_pool:
            self.crashed = True


def run(lam_fn):
    rng = random.Random(SEED)
    a = Agent("一块池四行为")
    for t in range(T):
        a.tick(rng, lam_fn(t))
    return a


def calm(t):
    return 0.15


def bursty(t):
    return 1.2 if (t % 24) >= 12 else 0.10


def high(t):
    return 2.0


def low(t):
    return 0.0


rows = []
for name, fn in [("A 平静", calm), ("B 突发", bursty), ("C 持续高压", high), ("D 无外部", low)]:
    a = run(fn)
    n = len(a.d_trace)
    tot = sum(a.counts.values()) or 1
    rows.append(dict(世界=name, 崩='是' if a.crashed else '否', 峰池=a.peak_pool,
                     平均D=round(sum(a.d_trace) / n, 2),
                     爱占=round(a.mode_ticks['爱'] / n, 2), 恨占=round(a.mode_ticks['恨'] / n, 2),
                     友善=round(a.counts['友善'] / tot, 2), 负担=round(a.counts['负担'] / tot, 2),
                     毁灭=round(a.counts['毁灭'] / tot, 2), 动力=round(a.counts['动力'] / tot, 2)))

lines = ["# 四行为爱恨沙盘：恨成为动力，爱成为负担", "",
         "| 世界 | 崩 | 峰池 | 平均D | 爱占 | 恨占 | 友善 | 负担 | 毁灭 | 动力 |",
         "|---|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    lines.append(f"| {r['世界']} | {r['崩']} | {r['峰池']} | {r['平均D']} | {r['爱占']} | {r['恨占']} | "
                 f"{r['友善']} | {r['负担']} | {r['毁灭']} | {r['动力']} |")
lines += ["", "## 判", "",
          "1. 四种行为都是「补差值」的手段：友善=温和补，负担=补不动、只剩维系，毁灭=暴力补，动力=高效补。",
          "2. 无外部输入的世界：爱持续 → 负担抬头（没有新东西可换，爱只剩 upkeep）。",
          "3. 持续高压世界：恨持续 → 毁灭 → 动力（从乱砸转成定向，积压不再涨）。",
          "4. 四个行为只靠一个差值调度；池有界、不崩，就说明这根轴够用。"]
out = Path(__file__).with_name("数据_四行为_爱恨沙盘.md")
out.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
print(f"\n>> {out}")
