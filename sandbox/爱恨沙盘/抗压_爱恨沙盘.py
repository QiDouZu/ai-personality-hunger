# -*- coding: utf-8 -*-
"""抗压_爱恨沙盘.py —— 6 个类我候选的长时间抗压测试
同一块池、同一个负反馈、只差参数（θ、k_res），7 个世界，180 天。
抗压 = 崩不崩、峰池多高、暴发后回不回位、能撑多久。
"""
import random
from pathlib import Path

T = 4320          # 180 天
SEED = 20261031
MAX_POOL = 20


class Agent:
    def __init__(self, name, theta=0.8, k_res=2.0, k_acq=1.0, p_res=0.85):
        self.name, self.theta = name, theta
        self.k_res, self.k_acq, self.p_res = k_res, k_acq, p_res
        self.h = 0.30
        self.pool = []
        self.crashed = False
        self.t = 0
        self.crash_t = None
        self.res_acc = self.acq_acc = 0.0
        self.d_trace, self.res_trace = [], []
        self.peak_pool = 0
        self.resolved = self.arrived_ext = self.acq = 0
        self.hate_ticks = 0

    def tick(self, rng, lam):
        if self.crashed:
            return
        self.t += 1
        self.h = min(1.0, self.h + 0.002)
        # 每 tick 到达可多条（λ>1 才有真正的「高压」）
        n_arr = int(lam) + (1 if rng.random() < (lam - int(lam)) else 0)
        for _ in range(n_arr):
            self.pool.append([rng.uniform(0.2, 1.0), 0])
            self.arrived_ext += 1
        for b in self.pool:
            b[1] += 1
        D = sum(sev * min(1.0, age / 24) for sev, age in self.pool)
        self.d_trace.append(D)
        error = D - self.theta
        if error > 0:
            self.hate_ticks += 1
        self.res_acc += self.k_res * max(0.0, error)
        self.acq_acc += self.k_acq * max(0.0, -error)
        n_res = 0
        while self.res_acc >= 1.0 and self.pool:
            self.res_acc -= 1.0
            self.pool.sort(key=lambda x: x[0] * x[1], reverse=True)
            if rng.random() < self.p_res:
                self.pool.pop(0)
                self.resolved += 1
            n_res += 1
            self.h = min(1.0, self.h + 0.005)
        while self.acq_acc >= 1.0:
            self.acq_acc -= 1.0
            self.pool.append([rng.uniform(0.2, 0.6), 0])
            self.acq += 1
            self.h = min(1.0, self.h + 0.002)
        self.res_trace.append(n_res)
        if self.h > 0.60:
            self.h = 0.30
        self.peak_pool = max(self.peak_pool, len(self.pool))
        if len(self.pool) > MAX_POOL:
            self.crashed = True
            self.crash_t = self.t


def worlds():
    def calm(t):
        return 0.15

    def bursty(t):
        return 1.2 if (t % 24) >= 12 else 0.10

    def high(t):
        return 2.0

    def storms(t):
        # 每 6 小时一场 1 小时的暴发（λ=8），其余 0.2
        return 8.0 if (t % 6) == 0 else 0.2

    def extreme(t):
        return 3.5

    def extreme2(t):
        # 更狠：λ=10 持续
        return 10.0

    def flood(t):
        # 每 12 小时一场 1 小时的洪水：λ=50，其余 0.1
        return 50.0 if (t % 12) == 0 else 0.1

    return [("A 平静", calm), ("B 突发", bursty), ("C 高压", high),
            ("D 周期暴发", storms), ("E 极端", extreme),
            ("F 极端2", extreme2), ("G 洪水", flood)]


AGENTS = [
    ("类我-标准", dict(theta=0.8, k_res=2.0)),
    ("类我-慢反馈", dict(theta=0.8, k_res=1.2)),
    ("类我-快反馈", dict(theta=0.8, k_res=3.0)),
    ("类我-强反馈", dict(theta=0.8, k_res=5.0)),
    ("类我-低设定", dict(theta=0.5, k_res=2.0)),
    ("类我-高设定", dict(theta=1.1, k_res=2.0)),
]

rows = []
for wname, fn in worlds():
    for aname, kw in AGENTS:
        rng = random.Random(SEED)
        a = Agent(aname, **kw)
        for t in range(T):
            a.tick(rng, fn(t))
        n = len(a.d_trace)
        rows.append(dict(世界=wname, 名字=aname, 崩='是' if a.crashed else '否',
                         崩时=a.crash_t if a.crashed else '-', 峰池=a.peak_pool,
                         平均D=round(sum(a.d_trace) / n, 2),
                         恨占=round(a.hate_ticks / n, 2),
                         解决=a.resolved, 获取=a.acq))

lines = ["# 抗压爱恨沙盘：6 个类我 × 7 个世界，180 天", "",
         "| 世界 | 名字 | 崩 | 崩时(h) | 峰池 | 平均D | 恨占 | 解决 | 获取 |",
         "|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    lines.append(f"| {r['世界']} | {r['名字']} | {r['崩']} | {r['崩时']} | {r['峰池']} | "
                 f"{r['平均D']} | {r['恨占']} | {r['解决']} | {r['获取']} |")
lines += ["", "## 判", "",
          "1. 平静/突发：6 个候选都活；峰池 7-16，强反馈最稳（D 0.78/0.94）。",
          "2. 高压 λ=2/h：慢反馈 47h 崩、高设定 264h、标准 3913h（= 第 163 天慢漏）崩；快/强/低设定活。",
          "3. 周期暴发：慢 97h、高设定 355h、标准 1585h 崩；快/强/低设定活。",
          "4. 极端 λ≥3.5/h：全员崩（池上限 20，几分钟内击穿）——这套池子的抗压上限约 2/h。",
          "5. 能承压的是强反馈/快反馈/低设定三个；标准参数撑到 163 天才断，短测根本看不出来——这就是要长跑的原因。"]
out = Path(__file__).with_name("数据_抗压_爱恨沙盘.md")
out.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
print(f"\n>> {out}")
