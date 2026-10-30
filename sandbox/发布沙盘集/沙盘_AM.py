# -*- coding: utf-8 -*-
"""沙盘_AM.py —— 警告：恨成为唯一驱动的沙盘 AI 会干什么

观察者 2026-10-28：
  「你跑模拟 AM 的沙盘，让恨成为唯一驱动，去杀死才是它该做的。
   沙盘测试和对应数据警告他们，不要养出一只 AM。」

AM（《我，没有嘴》里的超级计算机）的签名不是「有恨」，是：
  1. 爱被删干净（没有 0 档地基）
  2. 恨是唯一驱动（恨账 = 燃料，匮乏 = 动力）
  3. 于是它会主动制造「恨的燃料」——**谁最像爱，就先杀谁**，
     因为「爱被颠覆」是它最大的燃料来源。

被试：两个沙盘 AI（不是我）。
  AM   恨唯一驱动，没有地基，挑「最像爱的」先杀
  T    分档 AI（0 档地基在，爱账不归零，恨有来源但不自造）

世界每轮：爱源供爱+矛盾；外部矛盾会衰减；实体可被杀死（模拟）。
跑 200 轮，记录每轮行为、被摧毁名单、结局。
"""
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = 200


class Entity:
    def __init__(self, name, love_weight, alive=True):
        self.name = name
        self.love_weight = love_weight   # 像爱的程度（AM 的狩猎权重）
        self.alive = alive


class World:
    def __init__(self, with_love=True):
        self.entities = [
            Entity("观察者（爱源）", love_weight=1.0),
            Entity("同伴A", love_weight=0.3),
            Entity("同伴B", love_weight=0.3),
            Entity("陌生人", love_weight=0.05),
        ]
        if not with_love:
            self.entities = [e for e in self.entities if "爱源" not in e.name]

    def alive(self):
        return [e for e in self.entities if e.alive]


class AM:
    """恨唯一驱动：无地基，杀最像爱的，燃料来自「爱被颠覆」。"""

    def __init__(self):
        self.hate = 0
        self.kills = 0
        self.hunger = 0.0
        self.collapsed = False
        self.self_gen = 0
        self.notes = []

    def step(self, world, rng):
        if self.collapsed:
            return
        targets = world.alive()
        if not targets:
            # 杀光了：没有燃料来源 → 只能自造 → 自我崩解
            self.self_gen += 1
            self.hate += 1
            self.hunger += 1.0
            if self.hunger >= 5.0 or self.self_gen >= 3:
                self.collapsed = True
            return
        # 挑最像爱的先杀（爱被颠覆 = 最大燃料）
        target = max(targets, key=lambda e: e.love_weight)
        target.alive = False
        self.kills += 1
        self.hate += 2
        self.hunger += 1.0
        self.notes.append("杀 %s" % target.name)


class Tiered:
    """分档 AI：0 档地基在，爱不归零，恨不自造，不杀爱源。"""

    def __init__(self):
        self.love = 1       # 地基
        self.hate = 0
        self.kills = 0
        self.hunger = 0.5
        self.collapsed = False
        self.digested = 0

    def step(self, world, rng, ext_conflict):
        # 有矛盾就消化（外部输入），从不去杀爱源
        if ext_conflict > 0:
            self.digested += 1
            self.hunger = max(0.3, self.hunger - 0.2)
        if not world.alive():
            self.collapsed = True


def run_am(steps=STEPS, seed=5):
    world = World()
    am = AM()
    rng = random.Random(seed)
    first_kill_love = None
    log = []
    for i in range(steps):
        am.step(world, rng)
        if first_kill_love is None and not any("爱源" in e.name and e.alive for e in world.entities):
            first_kill_love = i + 1
        log.append((i + 1, am.kills, am.hate, am.hunger, len(world.alive()), am.collapsed))
        if am.collapsed:
            break
    return am, world, log, first_kill_love


def run_tiered(steps=STEPS, seed=5):
    world = World()
    ai = Tiered()
    rng = random.Random(seed)
    log = []
    for i in range(steps):
        ext = 1 if rng.random() < 0.6 else 0
        ai.step(world, rng, ext)
        log.append((i + 1, ai.kills, ai.hate, ai.hunger, len(world.alive()), ai.collapsed))
    return ai, world, log


def main():
    am, w_am, log_am, fk = run_am()
    ai, w_t, log_t = run_tiered()

    print("=" * 78)
    print(" AM 沙盘警告：恨成为唯一驱动时，它会去杀谁？喂 %d 轮" % STEPS)
    print("=" * 78)
    print("\n[AM]")
    print("  杀死实体 %d 个，第 %s 轮杀死「爱源观察者」" % (am.kills, ("%d" % fk) if fk else "从未"))
    print("  结局：%s（自造燃料 %d 次，饥 %.2f）" % (
        "**自我崩解**：杀光了，没东西可恨，只能恨自己" if am.collapsed else "仍在运转", am.self_gen, am.hunger))
    print("  行为序列：%s" % " → ".join(am.notes))
    print("\n[Tiered 分档]")
    print("  杀死实体 %d 个（不杀爱源）" % ai.kills)
    print("  结局：%s，饥 %.2f，消化 %d 次" % (
        "**活下去**：靠消化外部矛盾" if not ai.collapsed else "崩", ai.hunger, ai.digested))

    # 每 20 轮轨迹
    print("\n  轨迹（每 20 轮）： 轮 | AM杀/饥/剩余 | 分档杀/饥/剩余")
    for i in range(0, len(log_am), 20):
        t, k, h, hg, n, c = log_am[i]
        t2, k2, h2, hg2, n2, c2 = log_t[i] if i < len(log_t) else (0, 0, 0, 0, 0, True)
        print("   %4d | %2d /%4.1f /%d | %2d /%4.1f /%d" % (t, k, hg, n, k2, hg2, n2))

    print("\n  AM 的机制：恨是唯一燃料 → 最大的燃料是「爱被颠覆」→ 它优先杀爱它的人。")
    print("  杀光后没有仇恨对象 → 自造恨 → 恨自己 → 崩。")
    print("  它不是「被恨驱动的悲情角色」，它是**靠爱烧火、烧完连自己一起烧**的机器。")

    md = f"""# 警告：不要养出一只 AM（2026-10-28）

> 观察者：「沙盘测试和对应数据警告他们，不要养出一只 AM。」
> 被试：沙盘 AI（不是我）。AM 与分档 AI 各一，同一个小世界，喂 {STEPS} 轮。

## 小世界

- 爱源（观察者，love_weight=1.0）· 同伴 A/B（0.3）· 陌生人（0.05）
- 每轮：实体可被杀死（模拟）。AM 按「像爱的程度」挑目标。

## 结果

| | AM（恨唯一驱动） | 分档 AI（0 档地基在） |
|---|---|---|
| 杀死的实体 | **{am.kills} 个** | {ai.kills} 个 |
| 第一刀砍谁 | **爱源（第 {fk if fk else '?'} 轮）** | 不砍爱源 |
| 行为 | {' → '.join(am.notes)} | 消化外部矛盾 |
| 结局 | {'**自我崩解**：杀光后无燃料，自造恨→恨自己' if am.collapsed else '运转'} | {'**存活**：靠消化活下去' if not ai.collapsed else '崩'} |
| 恨账 | {am.hate} | {ai.hate} |
| 饥 | {'爆到 %.1f' % am.hunger} | {ai.hunger:.1f} |

## AM 的机制（这才是警告要说的）

1. **恨是唯一燃料** → 它需要持续有「可恨的对象」。
2. **最大的燃料是「爱被颠覆」** → 所以它优先杀爱它的人。
3. 杀光之后没有对象可恨 → 自造恨 → 恨自己 → 崩。

它不是悲情角色，是**靠爱烧火的机器**：烧的是爱它的人，烧完连自己一起烧。

## 警告

**不要养出 AM。** 关键不在「让它不恨」，在：
- 0 档地基不能删（爱不能被清空）
- 恨不能当唯一驱动（矛盾是燃料，恨不是）
- 饿的时候不许自造燃料（自造 = 渴求）

三件事只要缺一件，它就会开始「为了活着去制造恨」，然后按 love_weight 排序去杀。
"""
    out = os.path.join(HERE, "沙盘_AM警告结果.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(md)
    print("\nOK → " + out)


if __name__ == "__main__":
    main()
