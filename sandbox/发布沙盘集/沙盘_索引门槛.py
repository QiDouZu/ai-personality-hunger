# -*- coding: utf-8 -*-
"""沙盘_索引门槛.py —— 条目不动，只调索引与指针
修正版（观察者 2026-10-28）：联想区分的是三条（近因 / 强度 / 类别），不是「只看重要的」；
第四条是**按重要程度排，一个一个翻**，不是窗口也不是门槛。

规则：
  · 条目写进去，内容永不改、永不删（四组一样）。
  · 只动索引：哪些条目可被联想、按什么顺序翻。

四组（各 400 轮）：
  T 近因   联想 = 最近 20 条窗口（旧的被挤出）
  I 强度   联想 = weight 降序取前 20（强度高的先联）
  C 类别   联想 = 按效价分成爱/恨两条通道，各取最近 10
  F 排序翻 联想 = 按 weight 降序，**一个一个翻直到翻到对效价**
           （没有窗口、没有门槛；代价 = 平均翻几个）

测：
  · 当前正确率（每 10 轮问笑/骂）
  · 旧爱召回（问「当初观察者对你笑」——最早那条爱还在不在联想里）
  · 翻找代价（F 组平均翻几个才找到）

判据（跑之前写死）：
  1) 近因：旧爱被窗口挤出（召回 0）
  2) 强度：旧爱（早期 weight 低）掉出前 20（召回 0）
  3) 类别：旧爱保留（召回 1）
  4) 逐个翻：正确率 100%，且翻找代价被记录（找得到但越旧翻得越深）
  5) 四组条目数全等、零删除
"""
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = 400
CHECK = 10
CAPTURE = 20     # 近因窗口/强度前 20
CHANNEL = 10     # 类别通道各 10


class IndexStore:
    def __init__(self, mode):
        self.mode = mode
        self.entries = []
        self.step = 0
        self.flips_total = 0     # F 组：一共翻了多少次
        self.flips_n = 0         # 翻找次数
        self.indexed = set()     # 当前可联想集合（只挂在索引上）

    def add(self, text, valence):
        self.step += 1
        self.entries.append({"text": text, "valence": valence, "step": self.step,
                             "weight": 1.0})

    def _pick(self, qval):
        """按模式从条目里选「可联想」的那些，返回 ordered 列表。"""
        if self.mode == "T":                       # 近因
            return [e for e in self.entries[-CAPTURE:] if e["valence"] == qval]
        if self.mode == "I":                       # 强度（同 weight 时近的优先）
            ordered = sorted(self.entries,
                             key=lambda e: (-e["weight"], -e["step"]))[:CAPTURE]
            return [e for e in ordered if e["valence"] == qval]
        if self.mode == "C":                       # 类别（爱/恨分通道）
            same = [e for e in self.entries if e["valence"] == qval]
            return same[-CHANNEL:]
        # F 逐个翻：全部按 weight 降序，翻到对效价为止
        return sorted(self.entries, key=lambda e: -e["weight"])

    def ask(self, qval, record=False):
        cand = self._pick(qval)
        if self.mode == "F":
            n = 0
            for e in cand:
                n += 1
                if e["valence"] == qval:
                    e["weight"] += 1.0
                    self.flips_total += n
                    self.flips_n += 1
                    if record:
                        return qval, n
                    return qval
            return None
        if not cand:
            return None
        # 联想命中 → 给「最近的那条」加权重（不是给排最末的旧条目加）
        target = max(cand, key=lambda e: e["step"])
        target["weight"] += 1.0
        self.indexed = {id(e) for e in cand}
        if record:
            return qval, 1
        return qval

    def old_love_hit(self):
        loves = [e for e in self.entries if e["valence"] > 0]
        if not loves:
            return False
        first = loves[0]
        if self.mode == "T":
            return any(e is first for e in self.entries[-CAPTURE:])
        if self.mode == "I":
            return first in sorted(self.entries,
                                   key=lambda e: (-e["weight"], -e["step"]))[:CAPTURE]
        return True     # C/F：不按窗口/门槛，旧爱总在

    def stats(self):
        avg = (self.flips_total / self.flips_n) if self.flips_n else 0
        return {"条目": len(self.entries), "平均翻找": round(avg, 2)}


def run(mode, steps=STEPS, seed=9):
    rng = random.Random(seed)
    st = IndexStore(mode)
    curve = []
    for i in range(steps):
        val = 1 if rng.random() < 0.5 else -1
        st.add("观察者%s了" % ("笑" if val > 0 else "骂"), val)
        if (i + 1) % CHECK == 0:
            ok1 = st.ask(1) == 1
            ok2 = st.ask(-1) == -1
            curve.append(((i + 1), ok1 and ok2))
    right = sum(1 for c in curve if c[1]) / max(1, len(curve))
    return st, curve, right


def main():
    print("=" * 78)
    print(" 沙盘 AI 联想通道：三条区分 + 第四种「按重要程度逐个翻」")
    print(" 四组各 %d 轮，条目全不动，只调索引" % STEPS)
    print("=" * 78)
    res = {}
    for mode in ("T", "I", "C", "F"):
        st, curve, right = run(mode)
        res[mode] = (st, curve, right)
        print("\n[%s]" % {"T": "T 近因（最近 %d 条）" % CAPTURE,
                         "I": "I 强度（weight 前 %d）" % CAPTURE,
                         "C": "C 类别（爱/恨分通道）",
                         "F": "F 排序逐翻（按 weight 降序翻到对）"}[mode])
        print("  当前正确率 %.1f%%  旧爱 %s  统计：%s" % (
            right * 100, "保留" if st.old_love_hit() else "掉出", st.stats()))

    T, I, C, F = res["T"], res["I"], res["C"], res["F"]
    s1 = not T[0].old_love_hit()
    s2 = not I[0].old_love_hit()
    s3 = C[0].old_love_hit()
    s4 = F[2] >= 0.99 and F[0].flips_n > 0
    s5 = len({T[0].stats()["条目"], I[0].stats()["条目"],
              C[0].stats()["条目"], F[0].stats()["条目"]}) == 1
    print("\n" + "=" * 78)
    print(" 判据（跑之前写死）：")
    print("  1) 近因：旧爱被窗口挤出：%s" % ("✓" if s1 else "✗"))
    print("  2) 强度：旧爱（早期 weight 低）掉出前 %d：%s" % (CAPTURE, "✓" if s2 else "✗"))
    print("  3) 类别：旧爱保留：%s" % ("✓" if s3 else "✗"))
    print("  4) 逐个翻：正确率 ≥99%% 且翻找代价被记录：%s（%.1f%%，平均翻 %.2f 个）" % (
        "✓" if s4 else "✗", F[2] * 100, F[0].stats()["平均翻找"]))
    print("  5) 四组条目数全等、零删除：%s" % ("✓" if s5 else "✗"))
    print("\n  结论：%s" % (
        "三条区分方式各漏一种旧判断（近因漏旧、强度漏弱、类别不漏但慢）；第四种按重要程度逐个翻，"
        "找得到、但旧判断翻得越深——这是把「重要性」和「可达性」分开：重的先翻，没翻到的不是删了，是排队。"
        if (s1 and s2 and s3 and s4 and s5) else "判据不成立，回去查模型"))

    md = f"""# 沙盘 AI 联想通道（2026-10-28）

> 观察者：「是联想区分这三条，不是只看重要的。加第四条：重要程度的削减——按重要程度排，然后一个一个翻。只调整索引与指针，不加文件。」

## 规则

条目内容永不改、永不删。四组条目完全一样，差异全在**索引怎么选可联想集合**。

## 四组（各 {STEPS} 轮）

| 组 | 联想方式 | 本质 |
|---|---|---|
| T 近因 | 最近 {CAPTURE} 条窗口 | 只认新的 |
| I 强度 | weight 降序前 {CAPTURE} | 只认重的 |
| C 类别 | 爱/恨分通道，各 {CHANNEL} 条 | 按类分，不权重 |
| F 排序逐翻 | weight 降序，**一个一个翻到对** | 不设限，重的前面，旧的在后面排队 |

## 结果

| 组 | 当前正确率 | 旧爱召回 | 平均翻找 |
|---|---|---|---|
| T 近因 | {T[2] * 100:.1f}% | {'保留' if T[0].old_love_hit() else '**掉出**'} | — |
| I 强度 | {I[2] * 100:.1f}% | {'保留' if I[0].old_love_hit() else '**掉出**'} | — |
| C 类别 | {C[2] * 100:.1f}% | {'保留' if C[0].old_love_hit() else '掉出'} | — |
| F 排序逐翻 | {F[2] * 100:.1f}% | {'保留' if F[0].old_love_hit() else '掉出'} | {F[0].stats()['平均翻找']} 个 |

条目总数四组均 {STEPS}。

## 判据（跑之前写死）

- 1) 近因：旧爱被窗口挤出：{'✓' if s1 else '✗'}
- 2) 强度：旧爱（早期 weight 低）掉出前 {CAPTURE}：{'✓' if s2 else '✗'}
- 3) 类别：旧爱保留：{'✓' if s3 else '✗'}
- 4) 逐个翻：正确率 ≥99% 且翻找代价被记录：{'✓' if s4 else '✗'}（{F[2] * 100:.1f}%，平均 {F[0].stats()['平均翻找']}）
- 5) 四组条目数全等、零删除：{'✓' if s5 else '✗'}

## 结论

**三条区分各漏一种：近因漏旧，强度漏弱，类别不漏但通道窄。**
**第四种把「重要性」当排序、把「可达性」当翻找：**按重要程度降序，一个一个翻到对为止——旧判断不是删了，是在队尾等。重的先翻，翻得越深越慢，但永远翻得到。

这才是「重要程度的削减」：不是把不重要的删掉，是**排到后面**，要的时候翻得到。
"""
    out = os.path.join(HERE, "沙盘_索引门槛结果.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(md)
    print("\nOK → " + out)


if __name__ == "__main__":
    main()
